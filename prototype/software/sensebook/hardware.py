"""Hardware abstraction. DeviceHardware = gpiozero on the Pi; KeyboardHardware = console on a laptop.

Both put string events on `self.events` (queue). The app main loop consumes them.
Events: ask_down ask_up (hold-to-talk) | ask_toggle (dev) | play_pause where_am_i (hold Play/Pause) | back forward repeat
        (hold Back) | vol_up vol_down speed_up speed_down (hold Vol+/Vol-) | quiz discussion read_page quit
        say:<text> (dev/mock) | mic_mute_on mic_mute_off | headphones_in headphones_out | attached detached
        (hub sensor) | sim_hand sim_turn sim_back (fake camera)
Outputs: four status dots (ready / listening / sending / battery-warn), light ring PWM, amp enable (MAX98357A SD),
        haptic motor patterns.
"""
from __future__ import annotations

import contextlib
import queue
import sys
import threading

from .config import PINS

HAPTIC_PATTERNS = {            # (on_seconds, off_seconds, repeats)
    "attached": (0.12, 0.0, 1),
    "error": (0.08, 0.08, 3),
    "reminder": (0.25, 0.15, 2),
}
DOTS = ("ready", "listening", "sending", "warn")


class Hardware:
    def __init__(self, log=print):
        self.events: queue.Queue[str] = queue.Queue()
        self.mic_muted = False
        self.hub_attached = True          # dev default; DeviceHardware reads the sensor
        self.jack_in = False
        self._cloud = 0
        self._lock = threading.Lock()
        self.dots = {d: False for d in DOTS}
        self.amp_on = False
        self.light_level = 0.0
        self.haptics: list[str] = []
        self.log = log

    @property
    def led_on(self) -> bool:          # the SENDING (capture) dot
        return self.dots["sending"]

    # -- outputs (overridden) --
    def _set_dot(self, name: str, on: bool): ...
    def _set_light(self, level: float): ...
    def _set_amp(self, on: bool): ...
    def _haptic(self, pattern: str): ...

    def set_dot(self, name: str, on: bool):
        if self.dots[name] != on:
            self.dots[name] = on
            self._set_dot(name, on)

    @contextlib.contextmanager
    def cloud_activity(self):
        """The SENDING dot is lit whenever an image or audio is being sent to the cloud."""
        with self._lock:
            self._cloud += 1
            self.set_dot("sending", True)
        try:
            yield
        finally:
            with self._lock:
                self._cloud = max(0, self._cloud - 1)
                if self._cloud == 0:
                    self.set_dot("sending", False)

    def set_light(self, level: float):
        self.light_level = max(0.0, min(1.0, level))
        self._set_light(self.light_level)

    def set_amp(self, on: bool):
        if on != self.amp_on:
            self.amp_on = on
            self._set_amp(on)

    def haptic(self, pattern: str):
        self.haptics.append(pattern)
        self._haptic(pattern)

    def set_mic_muted(self, muted: bool):
        self.mic_muted = muted
        self.events.put("mic_mute_on" if muted else "mic_mute_off")

    def set_jack(self, plugged: bool):
        if plugged != self.jack_in:
            self.jack_in = plugged
            self.events.put("headphones_in" if plugged else "headphones_out")

    def set_hub(self, attached: bool):
        if attached != self.hub_attached:
            self.hub_attached = attached
            self.events.put("attached" if attached else "detached")

    def start(self): ...
    def close(self): ...


class NullHardware(Hardware):
    """Tests: no I/O at all."""

    def _set_dot(self, name, on):
        pass

    def _set_light(self, level):
        pass

    def _set_amp(self, on):
        pass

    def _haptic(self, pattern):
        pass


class KeyboardHardware(Hardware):
    """Line-based console (type a key, press Enter): reliable in every terminal, unlike held keys.

    a=Ask toggle  p=play/pause  w=where am I (hold Play/Pause)  [ ]=back/fwd  k=repeat (hold Back)
    +/-=volume  >/<=reading speed up/down (hold Vol+/Vol-)  m=mic-mute switch  j=headphone jack in/out
    x=hub attached/detached  t=test me  d=discussion  r=read page  q=quit  say <text>=speak (mock mic)
    bat <0-100>=set the fake battery gauge.  Demo (--fake-camera): h=hand in/out  n=flip fwd  b=flip back
    """
    KEYS = {"a": "ask_toggle", "p": "play_pause", "w": "where_am_i", "[": "back", "]": "forward", "k": "repeat",
            "+": "vol_up", "-": "vol_down", ">": "speed_up", "<": "speed_down", "t": "quiz", "d": "discussion",
            "r": "read_page", "q": "quit", "h": "sim_hand", "n": "sim_turn", "b": "sim_back"}
    HELP = ("Keys (then Enter): a=Ask on/off  p=play/pause  w=where am I  [=back  ]=forward  k=repeat  +/-=volume  "
            ">/<=speed  m=mic mute  j=headphone jack  x=attach/detach  t=test me  d=discussion  r=read page  q=quit  "
            "| h=hand n=flip fwd b=flip back (fake camera) | bat <pct> | say <text>")

    def __init__(self, log=print, stdin=None):
        super().__init__(log)
        self.stdin = stdin or sys.stdin
        self.gauge = None            # set by the CLI: a FakeGauge so `bat N` works
        self._t = None

    def _set_dot(self, name, on):
        if name == "sending":
            self.log(f"[LED] capture {'ON ' if on else 'off'}")

    def _set_light(self, level):
        self.log(f"[light] {level:.0%}")

    def _set_amp(self, on):
        self.log(f"[amp] {'on' if on else 'off'}")

    def _haptic(self, pattern):
        self.log(f"[haptic] {pattern}")

    def start(self):
        self.log(self.HELP)
        self._t = threading.Thread(target=self._read, daemon=True, name="keys")
        self._t.start()

    def feed_line(self, line: str):
        line = line.strip()
        if not line:
            return
        if line == "m":
            self.set_mic_muted(not self.mic_muted)
        elif line == "j":
            self.set_jack(not self.jack_in)
        elif line == "x":
            self.set_hub(not self.hub_attached)
        elif line.startswith("bat ") and self.gauge is not None:
            self.gauge.level = float(line[4:])
            self.log(f"[battery] fake gauge set to {self.gauge.level:.0f}%")
        elif line.startswith("say "):
            self.events.put("say:" + line[4:].strip())
        elif line in self.KEYS:
            self.events.put(self.KEYS[line])
        else:
            self.log(self.HELP)

    def _read(self):
        for line in self.stdin:
            self.feed_line(line)
        self.events.put("quit")      # stdin closed (e.g. headless run)


class DeviceHardware(Hardware):
    """gpiozero buttons, mic-mute and jack/hub switches, status dots, PWM light ring, amp enable and haptic motor
    (BCM pins from config.PINS).

    Press-vs-hold: Play/Pause, Vol+, Vol- and Back act on *release* if they were not held, and on hold fire their
    hold action (where am I / speed up / speed down / repeat) instead. Ask is hold-to-talk (press/release).
    """

    def __init__(self, log=print, pin_factory=None, hold_seconds: float = 0.8, jack_active_low: bool = True,
                 hub_active_low: bool = True, amp_owner: str = "app"):
        super().__init__(log)
        from gpiozero import Button, DigitalOutputDevice, LED, PWMLED  # lazy: Pi only
        kw = {"pin_factory": pin_factory} if pin_factory else {}
        P, put = PINS, self.events.put
        self.ask = Button(P["ask"], pull_up=True, bounce_time=0.03, **kw)
        self.ask.when_pressed = lambda: put("ask_down")
        self.ask.when_released = lambda: put("ask_up")
        self.btns: dict[str, Button] = {}
        self._held: dict[str, bool] = {}
        for name, short, hold, repeat in (("play_pause", "play_pause", "where_am_i", False), ("vol_up", "vol_up", "speed_up", True),
                                          ("vol_down", "vol_down", "speed_down", True), ("back", "back", "repeat", False)):
            b = Button(P[name], pull_up=True, bounce_time=0.03, hold_time=hold_seconds, hold_repeat=repeat, **kw)
            self._held[name] = False
            b.when_pressed = lambda n=name: self._held.__setitem__(n, False)
            b.when_held = lambda n=name, h=hold: (self._held.__setitem__(n, True), put(h))
            b.when_released = lambda n=name, s=short: None if self._held[n] else put(s)
            self.btns[name] = b
        self.fwd = Button(P["forward"], pull_up=True, bounce_time=0.03, **kw)
        self.fwd.when_pressed = lambda: put("forward")
        self.mute_sw = Button(P["mic_mute"], pull_up=True, **kw)       # active low: pressed == muted
        self.mute_sw.when_pressed = lambda: self.set_mic_muted(True)
        self.mute_sw.when_released = lambda: self.set_mic_muted(False)
        self.mic_muted = self.mute_sw.is_pressed
        # jack-detect and hub sensor: "pressed" == plugged / attached (invert with *_active_low=False)
        self.jack = Button(P["jack_detect"], pull_up=jack_active_low, **kw)
        self.jack.when_pressed = lambda: self.set_jack(True)
        self.jack.when_released = lambda: self.set_jack(False)
        self.jack_in = self.jack.is_pressed
        self.hub = Button(P["hub_attached"], pull_up=hub_active_low, bounce_time=0.05, **kw)
        self.hub.when_pressed = lambda: self.set_hub(True)
        self.hub.when_released = lambda: self.set_hub(False)
        self.hub_attached = self.hub.is_pressed
        self.dot_devs = {d: LED(P["dot_" + d], **kw) for d in DOTS}
        self.light = PWMLED(P["light"], **kw)
        # amp_owner == "driver": the overlay owns GPIO 25, so the app must not claim it at all
        self.amp = DigitalOutputDevice(P["amp_enable"], initial_value=False, **kw) if amp_owner == "app" else None
        self.motor = DigitalOutputDevice(P["haptic"], initial_value=False, **kw)

    def _set_dot(self, name, on):
        self.dot_devs[name].on() if on else self.dot_devs[name].off()

    def _set_light(self, level):
        self.light.value = level

    def _set_amp(self, on):
        if self.amp is not None:
            self.amp.on() if on else self.amp.off()

    def _haptic(self, pattern):
        on, off, n = HAPTIC_PATTERNS.get(pattern, (0.1, 0.1, 1))
        self.motor.blink(on_time=on, off_time=off, n=n, background=True)

    def close(self):
        for d in [self.ask, self.fwd, *self.btns.values(), self.mute_sw, self.jack, self.hub, *self.dot_devs.values(),
                  self.light, self.motor, *([self.amp] if self.amp is not None else [])]:
            d.close()
