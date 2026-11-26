"""Google Gemini provider (google-genai SDK). All model IDs and voices come from config.

Call shapes follow the ai.google.dev docs as read in Nov 2026:
  * text / vision / audio-in / function calling: client.models.generate_content + types.Part.from_bytes
  * TTS: Interactions API (client.interactions.create, response_format audio, speech_config speakers),
    with automatic fallback to generate_content(response_modalities=["AUDIO"], SpeechConfig).
NOT exercised against the live API in the build session (no key): see README "Verification status".
"""
from __future__ import annotations

import base64
import json
import os
import re

from ..audio import pcm_to_wav
from ..pages import PageContent
from .base import (AudioClip, ProviderError, ProviderUnavailable, Speech, ToolCall, Tutor, TutorContext,
                   TutorReply, VisionReader)

LANG_NAME = {"bn": "Bangla (Bengali)", "en": "English"}


def _client(api_key: str | None):
    from google import genai
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ProviderError("GEMINI_API_KEY is not set (see .env.example)")
    return genai.Client(api_key=key)


_KEY_RE = re.compile(r"AIza[0-9A-Za-z_\-]{20,}|key=[^&\s]+", re.I)


def redact(text: str) -> str:
    """Never let an API key reach logs, spoken output or exceptions."""
    text = _KEY_RE.sub("[REDACTED]", text)
    k = os.environ.get("GEMINI_API_KEY")
    return text.replace(k, "[REDACTED]") if k else text


def _wrap(fn):
    """Map transport failures to ProviderUnavailable so the app can degrade gracefully."""
    def inner(*a, **k):
        try:
            return fn(*a, **k)
        except ProviderError:
            raise
        except Exception as e:  # SDK raises httpx / genai.errors.*
            name = type(e).__name__.lower() + str(e).lower()
            if any(t in name for t in ("connect", "timeout", "network", "resolve", "unreachable", "503", "unavailable")):
                raise ProviderUnavailable(redact(str(e))) from None
            raise ProviderError(redact(str(e))) from None
    return inner


def _json(text: str):
    t = text.strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    return json.loads(t)


class GeminiBase:
    def __init__(self, cfg: dict, api_key: str | None = None, client=None):
        self.cfg = cfg["gemini"]
        self.client = client or _client(api_key)

    def _gen(self, contents, system=None, tools=None, json_out=False, temperature=0.3):
        from google.genai import types
        kw = dict(system_instruction=system, temperature=temperature)
        if json_out:
            kw["response_mime_type"] = "application/json"
        if tools:
            kw["tools"] = [types.Tool(function_declarations=[
                types.FunctionDeclaration(name=t["name"], description=t["description"],
                                          parameters_json_schema=t["parameters"]) for t in tools])]
            kw["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(disable=True)
        return self.client.models.generate_content(
            model=self.cfg["text_model"], contents=contents, config=types.GenerateContentConfig(**kw))

    @staticmethod
    def _parts_for(q: "AudioClip | str"):
        from google.genai import types
        if isinstance(q, str):
            return [q]
        return [types.Part.from_bytes(data=q.wav, mime_type="audio/wav")]


class GeminiVision(GeminiBase, VisionReader):
    PROMPT = (
        "You are the eyes of a reading device for students, including blind readers. Transcribe the printed page "
        "in the image FAITHFULLY, in reading order (headings, paragraphs, list items, figure captions). "
        "Copy text exactly as printed in its original script (Bangla or English). Do NOT correct, translate, "
        "summarise or add anything. If any character, digit or word cannot be read with certainty, write the "
        "placeholder ‹?› at that spot and add the nearby word to that block's `uncertain` list; never guess. "
        "Ignore running headers/page furniture except the printed page number. "
        "The image comes from an ultra-wide camera: the far (top) edge of the page is squashed, so be especially careful with small print and mark doubtful characters. "
        "Report `orientation` of the printed text. If the page is blurry, cut off, glared or empty, set `problem` to one of blurry|cut_off|glare|no_text "
        "and return fewer blocks. Return JSON only: "
        '{"page_number": string|null, "language": "bn"|"en"|"mixed", "orientation": "upright"|"upside_down"|"sideways", "confidence": number 0..1, '
        '"problem": null|string, "blocks": [{"type": "heading|paragraph|list_item|caption|other", '
        '"text": string, "uncertain": [string]}]}')

    @_wrap
    def read_page(self, jpeg: bytes, lang_hint: str = "bn") -> PageContent:
        from google.genai import types
        r = self._gen([types.Part.from_bytes(data=jpeg, mime_type="image/jpeg"), self.PROMPT],
                      json_out=True, temperature=0.0)
        try:
            return PageContent.from_dict(_json(r.text))
        except (ValueError, TypeError) as e:
            raise ProviderError(f"unparseable page JSON: {e}")


class GeminiTutor(GeminiBase, Tutor):
    def _system(self, ctx: TutorContext) -> str:
        return (
            f"You are SenseBook, a patient study tutor for a Bangladeshi secondary-school student "
            f"(NCTB curriculum). Reply in {LANG_NAME[ctx.lang]}, in short spoken sentences with no markdown. "
            "Ground every answer in the PAGE text below. If the answer is not on the page, say so plainly "
            "before offering general help. NEVER invent citations, page numbers or quotes. Explain at the "
            f"learner's level ({ctx.memory.get('level', 'class 9')}). "
            "Use the provided tools when the user asks to set a reminder, remember or forget something, "
            "start a quiz or discussion, read the page, bookmark or change language. "
            f"Current local time: {ctx.now_local} ({ctx.timezone}). Resolve relative times from it.\n\n"
            f"PAGE:\n{ctx.page_text}\n\nRECENT PAGES:\n" + "\n---\n".join(ctx.recent_pages[-3:]) +
            f"\n\nMEMORY (opt-in, may be empty): {json.dumps(ctx.memory, ensure_ascii=False)}")

    @_wrap
    def answer(self, question, ctx):
        from ..tutor import TOOLS
        contents = []
        for role, text in ctx.history[-6:]:
            contents.append(f"{role}: {text}")
        contents += self._parts_for(question)
        r = self._gen(contents, system=self._system(ctx), tools=TOOLS)
        calls = [ToolCall(c.name, dict(c.args or {})) for c in (getattr(r, "function_calls", None) or [])]
        try:
            text = r.text or ""
        except Exception:
            text = ""
        return TutorReply(text.strip(), calls)

    def _json_task(self, prompt: str, parts=()):
        r = self._gen([*parts, prompt], json_out=True, temperature=0.4)
        try:
            return _json(r.text)
        except ValueError as e:
            raise ProviderError(f"unparseable JSON: {e}")

    @_wrap
    def make_quiz(self, pages_text, lang, level, n_mcq=3, n_short=2):
        return self._json_task(
            f"From ONLY the text below, write {n_mcq} multiple-choice and {n_short} short-answer questions in "
            f"{LANG_NAME[lang]} for a {level} student. Questions must be answerable from the text. Return a JSON list of "
            '{"type":"mcq"|"short","question":str,"options":[4 strings, mcq only],"answer":"A|B|C|D for mcq, model answer for short",'
            '"answer_text":str,"concept":short concept name,"explanation":one sentence}.\n\nTEXT:\n' + pages_text)

    @_wrap
    def grade(self, question, answer, lang):
        prompt = (f"Grade the student's spoken/typed answer in {LANG_NAME[lang]}. Question: {question['question']} "
                  f"Options: {question.get('options')} Reference answer: {question['answer']} / {question.get('answer_text','')}. "
                  'Be fair: accept paraphrases. Return JSON {"heard": transcript of what the student said, '
                  '"score": 0..1, "correct": bool, "feedback": one or two short spoken sentences with the right answer if wrong}.')
        return self._json_task(prompt, self._parts_for(answer))

    @_wrap
    def make_script(self, pages_text, lang, minutes):
        words = minutes * 130 if lang == "en" else minutes * 110
        return self._json_task(
            f"Write a podcast-style two-host discussion in {LANG_NAME[lang]}, about {words} words (~{minutes} minutes), "
            "of the text below. Hosts: `learner` (curious, asks questions, sometimes confused) and `teacher` "
            "(clear, uses examples, corrects mistakes gently). Stay faithful to the text; do not invent facts. "
            'Return a JSON list of {"speaker":"learner"|"teacher","text":str}. TEXT:\n' + pages_text)

    @_wrap
    def host_reply(self, script_so_far, question, lang):
        ctx = "\n".join(f"{l['speaker']}: {l['text']}" for l in script_so_far[-12:])
        return self._json_task(
            f"The listener interrupted the two-host discussion with the question you hear/read. Continue in {LANG_NAME[lang]}: "
            "the hosts (`learner`,`teacher`) answer in character in 3-6 short lines, grounded in the discussion. "
            'Return a JSON list of {"speaker":..., "text":...}. Discussion so far:\n' + ctx, self._parts_for(question))


class GeminiSpeech(GeminiBase, Speech):
    def __init__(self, cfg, api_key=None, client=None):
        super().__init__(cfg, api_key, client)
        self.sample_rate = int(self.cfg.get("tts_sample_rate", 24000))
        self.voices = self.cfg["voices"]

    STYLE = {
        "reader": "Read the following text aloud verbatim, in a calm, neutral, clear reading voice. Do not add, skip or change any word",
        "explainer": "Say the following warmly, like a friendly tutor",
    }

    def _pace(self, speed):
        return "slowly" if speed < 0.85 else "quickly" if speed > 1.15 else "at a natural pace"

    @_wrap
    def synthesize(self, text, role, lang, speed=1.0):
        voice = self.voices["reader" if role == "reader" else "explainer"]
        prompt = f"{self.STYLE.get(role, self.STYLE['explainer'])}, speaking {self._pace(speed)}:\n{text}"
        return self._tts_single(prompt, voice)

    @_wrap
    def synthesize_dialogue(self, lines, lang):
        names = {"learner": "Learner", "teacher": "Teacher"}
        voices = {"Learner": self.voices["host_learner"], "Teacher": self.voices["host_teacher"]}
        script = "\n".join(f"{names.get(l['speaker'], 'Teacher')}: {l['text']}" for l in lines)
        prompt = "Perform this as a lively two-person podcast conversation:\n" + script
        return self._tts_multi(prompt, voices)

    # ---- two API shapes ----
    def _tts_single(self, prompt, voice):
        if self.cfg.get("tts_api") == "interactions":
            try:
                it = self.client.interactions.create(
                    model=self.cfg["tts_model"], input=prompt, response_format={"type": "audio"},
                    generation_config={"speech_config": [{"voice": voice}]})
                return self._wav(base64.b64decode(it.output_audio.data))
            except Exception as e:
                if _is_net(e):
                    raise
        return self._legacy(prompt, single=voice)

    def _tts_multi(self, prompt, voices: dict):
        if self.cfg.get("tts_api") == "interactions":
            try:
                it = self.client.interactions.create(
                    model=self.cfg["tts_model"], input=prompt, response_format={"type": "audio"},
                    generation_config={"speech_config": {"speakers": [{"speaker": k, "voice": v} for k, v in voices.items()]}})
                return self._wav(base64.b64decode(it.output_audio.data))
            except Exception as e:
                if _is_net(e):
                    raise
        return self._legacy(prompt, multi=voices)

    def _legacy(self, prompt, single=None, multi=None):
        from google.genai import types
        if multi:
            sc = types.SpeechConfig(multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(speaker_voice_configs=[
                types.SpeakerVoiceConfig(speaker=k, voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=v))) for k, v in multi.items()]))
        else:
            sc = types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=single)))
        r = self.client.models.generate_content(
            model=self.cfg["tts_model"], contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=sc))
        data = r.candidates[0].content.parts[0].inline_data.data
        return self._wav(data)

    def _wav(self, data: bytes) -> bytes:
        if data[:4] == b"RIFF":
            return data
        import numpy as np
        return pcm_to_wav(np.frombuffer(data, dtype="<i2"), self.sample_rate)   # raw 24 kHz s16le mono


def _is_net(e: Exception) -> bool:
    s = (type(e).__name__ + str(e)).lower()
    return any(t in s for t in ("connect", "timeout", "resolve", "network"))
