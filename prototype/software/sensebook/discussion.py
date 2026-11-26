"""Chapter Talk: two-host script -> multi-speaker TTS -> interruptible playback."""
from __future__ import annotations

from .audio import Player


class Discussion:
    """Segments are rendered lazily so playback starts after the first segment, not after the whole script."""

    def __init__(self, tutor, speech, player: Player, lang: str, segment_lines: int = 6):
        self.tutor, self.speech, self.player, self.lang, self.seg = tutor, speech, player, lang, segment_lines
        self.script: list[dict] = []
        self.pos = 0                 # next segment index
        self.interrupted = False

    def prepare(self, pages_text: str, minutes: int = 4):
        self.script = self.tutor.make_script(pages_text, self.lang, minutes)
        self.pos = 0
        return self.script

    @property
    def n_segments(self) -> int:
        return -(-len(self.script) // self.seg)

    def finished(self) -> bool:
        return self.pos >= self.n_segments

    def play(self) -> bool:
        """Play from the current segment. Returns True if completed, False if interrupted."""
        self.interrupted = False
        while not self.finished():
            lines = self.script[self.pos * self.seg:(self.pos + 1) * self.seg]
            wav = self.speech.synthesize_dialogue(lines, self.lang)
            if not self.player.play(wav):
                self.interrupted = True       # re-play this segment on resume (cheap, keeps context)
                return False
            self.pos += 1
        return True

    def answer_interruption(self, question) -> bool:
        """Hosts answer the user's question in character, then control returns (caller offers resume)."""
        played = self.script[: (self.pos + 1) * self.seg]
        lines = self.tutor.host_reply(played, question, self.lang)
        wav = self.speech.synthesize_dialogue(lines, self.lang)
        return self.player.play(wav)
