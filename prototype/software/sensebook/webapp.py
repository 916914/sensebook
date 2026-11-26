"""Companion web app (Flask, plain HTML/CSS/JS), PIN-protected, LAN port 8080."""
from __future__ import annotations

import os
import secrets
import time
from datetime import datetime, timezone

from flask import (Flask, Response, abort, flash, redirect, render_template, request, session, url_for)

from .reminders import ReminderError, parse_local

NAV = [("dashboard", "Dashboard"), ("memory", "Notes & memory"), ("reminders", "Reminders"),
       ("quizzes", "Quiz history"), ("library", "Library"), ("settings", "Settings")]


def create_app(app_core, secret: str | None = None) -> Flask:
    """app_core is the SenseBookApp (or any object with .memory, .reminders, .cache, .tracker, .clock, .tz)."""
    web = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    web.secret_key = secret or os.environ.get("SENSEBOOK_SECRET") or secrets.token_hex(32)
    web.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    mem = app_core.memory
    fails = {"n": 0, "until": 0.0}

    def csrf() -> str:
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return session["csrf"]

    web.jinja_env.globals.update(csrf=csrf, NAV=NAV)

    @web.before_request
    def gate():
        ep = request.endpoint
        if ep in ("static", "login", "setup"):
            return
        if not mem.pin_is_set():
            return redirect(url_for("setup"))
        if not session.get("ok"):
            return redirect(url_for("login"))
        if request.method == "POST" and not secrets.compare_digest(request.form.get("csrf", ""), session.get("csrf", "x")):
            abort(400)

    @web.after_request
    def headers(r):
        r.headers["X-Frame-Options"] = "DENY"
        r.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'"
        r.headers["Cache-Control"] = "no-store"
        return r

    # ---------------- auth
    @web.route("/setup", methods=["GET", "POST"])
    def setup():
        if mem.pin_is_set():
            return redirect(url_for("login"))
        if request.method == "POST":
            try:
                mem.set_pin(request.form.get("pin", ""))
            except ValueError as e:
                flash(str(e), "error")
            else:
                session["ok"] = True
                return redirect(url_for("dashboard"))
        return render_template("auth.html", title="Set a guardian PIN", setup=True)

    @web.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            if time.time() < fails["until"]:
                flash("Too many attempts. Wait a minute.", "error")
            elif mem.check_pin(request.form.get("pin", "")):
                fails["n"] = 0
                session["ok"] = True
                return redirect(url_for("dashboard"))
            else:
                fails["n"] += 1
                if fails["n"] >= 5:
                    fails["until"], fails["n"] = time.time() + 60, 0
                flash("Wrong PIN.", "error")
        return render_template("auth.html", title="Enter guardian PIN", setup=False)

    @web.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # ---------------- pages
    @web.route("/")
    def dashboard():
        today = app_core.clock().astimezone(app_core.tz).strftime("%Y-%m-%d")
        st = mem.stats(app_core.clock().strftime("%Y-%m-%d")) if mem.enabled else None
        return render_template("dashboard.html", title="Dashboard", stats=st, mem_on=mem.enabled,
                               due=app_core.tracker.due() if mem.enabled else [],
                               concepts=app_core.tracker.all() if mem.enabled else [], today=today)

    @web.route("/memory", methods=["GET", "POST"])
    def memory():
        if request.method == "POST":
            act = request.form.get("action")
            if act == "delete_note":
                mem.delete_note(int(request.form["id"]))
                flash("Note deleted.", "ok")
            elif act == "delete_all":
                if mem.check_pin(request.form.get("pin", "")):
                    mem.delete_everything()
                    flash("Everything was deleted.", "ok")
                else:
                    flash("Wrong PIN: nothing deleted.", "error")
            return redirect(url_for("memory"))
        return render_template("memory.html", title="Notes & memory", notes=mem.list_notes(),
                               bookmarks=mem.list_bookmarks(), mem_on=mem.enabled, summary=mem.spoken_summary())

    @web.route("/export.json")
    def export():
        return Response(mem.export_json(), mimetype="application/json",
                        headers={"Content-Disposition": "attachment; filename=sensebook-export.json"})

    @web.route("/reminders", methods=["GET", "POST"])
    def reminders():
        if request.method == "POST":
            act, f = request.form.get("action"), request.form
            try:
                if act == "delete":
                    app_core.reminders.delete(int(f["id"]))
                    flash("Reminder deleted.", "ok")
                elif act in ("create", "edit"):
                    when = parse_local(f["when"], app_core.tz)
                    if act == "create":
                        app_core.reminders.from_tool_args({"message": f["message"], "datetime_local": f["when"],
                                                           "repeat": f.get("repeat", "none")})
                        flash("Reminder created.", "ok")
                    else:
                        app_core.reminders.update(int(f["id"]), f["message"], when, f.get("repeat", "none"), active=True)
                        flash("Reminder updated.", "ok")
            except (ReminderError, KeyError, ValueError) as e:
                flash(f"Could not save: {e}", "error")
            return redirect(url_for("reminders"))
        items = [{"r": r, "local": r.next_fire.astimezone(app_core.tz).strftime("%Y-%m-%dT%H:%M") if r.next_fire else ""}
                 for r in app_core.reminders.list()]
        return render_template("reminders.html", title="Reminders", items=items)

    @web.route("/quizzes")
    def quizzes():
        return render_template("quizzes.html", title="Quiz history", rows=mem.quiz_history(), mem_on=mem.enabled)

    @web.route("/library")
    def library():
        return render_template("library.html", title="Library", rows=app_core.cache.library())

    @web.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            f = request.form
            if f.get("action") == "pin":
                if mem.check_pin(f.get("old_pin", "")):
                    try:
                        mem.set_pin(f.get("new_pin", ""))
                        flash("PIN changed.", "ok")
                    except ValueError as e:
                        flash(str(e), "error")
                else:
                    flash("Current PIN is wrong.", "error")
            else:
                lang = f.get("language", "bn")
                mem.set("language", lang if lang in ("bn", "en") else "bn")
                mem.set("voice_speed", min(1.4, max(0.7, float(f.get("voice_speed", 1.0)))))
                mem.set_enabled(f.get("memory_enabled") == "on")
                pref = f.get("headphone_pref", "speaker")
                mem.set("headphone_pref", pref if pref in ("speaker", "headphones", "bluetooth") else "speaker")
                mem.set("light_level", min(1.0, max(0.0, float(f.get("light_level", 0.4)))))
                mem.set("accessibility_mode", "1" if f.get("accessibility_mode") == "on" else "0")
                mem.set("level", f.get("level", "class 9")[:40])
                mem.set("current_book", f.get("current_book", "My book")[:80])
                if hasattr(app_core, "apply_settings"):
                    app_core.apply_settings()
                flash("Settings saved.", "ok")
            return redirect(url_for("settings"))
        g = mem.get
        return render_template("settings.html", title="Settings", s={
            "language": g("language"), "voice_speed": g("voice_speed"), "memory_enabled": mem.enabled,
            "headphone_pref": g("headphone_pref"), "light_level": g("light_level"), "level": g("level"),
            "current_book": g("current_book"), "accessibility_mode": g("accessibility_mode") == "1"})

    return web
