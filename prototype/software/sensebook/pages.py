"""Page model, perceptual hash and the SQLite page cache (a seen page is never re-sent to the cloud)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

import cv2
import numpy as np

from .db import Database


def phash(img: np.ndarray) -> str:
    """64-bit DCT perceptual hash as 16 hex chars. Accepts BGR or gray uint8."""
    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    d = cv2.dct(g)[:8, :8]
    bits = (d > np.median(d.flatten()[1:])).flatten()
    return "%016x" % int("".join("1" if b else "0" for b in bits), 2)


def hamming(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


@dataclass
class Block:
    type: str            # heading | paragraph | caption | list_item | other
    text: str
    uncertain: list[str] = field(default_factory=list)


@dataclass
class PageContent:
    blocks: list[Block]
    lang: str = "en"
    confidence: float = 1.0
    page_label: str | None = None
    problem: str | None = None      # None | blurry | cut_off | glare | no_text | dark | blocked
    page_id: int | None = None
    from_cache: bool = False
    upside_down: bool = False       # vision model saw the print upside down (book attached the wrong way up)

    @property
    def ok(self) -> bool:
        return self.problem is None and bool(self.blocks)

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks)

    def to_json(self) -> str:
        return json.dumps({"blocks": [asdict(b) for b in self.blocks], "lang": self.lang,
                           "confidence": self.confidence, "page_label": self.page_label}, ensure_ascii=False)

    @staticmethod
    def from_dict(d: dict) -> "PageContent":
        blocks = [Block(b.get("type", "paragraph"), b.get("text", ""), list(b.get("uncertain", []) or []))
                  for b in d.get("blocks", [])]
        pc = PageContent(blocks, d.get("lang") or d.get("language") or "en",
                         float(d.get("confidence", 1.0)), d.get("page_label") or d.get("page_number"),
                         d.get("problem"))
        pc.upside_down = bool(d.get("upside_down")) or d.get("orientation") == "upside_down"
        return pc


_BN_DIGITS = str.maketrans("\u09e6\u09e7\u09e8\u09e9\u09ea\u09eb\u09ec\u09ed\u09ee\u09ef", "0123456789")


def label_number(label) -> int | None:
    """Printed page label -> int (handles Bangla digits); None if absent/non-numeric."""
    if label is None:
        return None
    m = re.search(r"\d+", str(label).translate(_BN_DIGITS))
    return int(m.group()) if m else None


UNCERTAIN_MARK = "‹?›"   # ‹?›


_SENT_SPLIT = re.compile(r"(?<=[.!?।])\s+")


def split_sentences(text: str) -> list[str]:
    """Sentence split for English (. ! ?) and Bangla (danda)."""
    return [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]


def reading_units(page: PageContent) -> list[tuple[int, str]]:
    """(block_index, sentence) in reading order; uncertain marks are kept so the reader can say 'unclear'."""
    units = []
    for i, b in enumerate(page.blocks):
        for s in (split_sentences(b.text) if b.type not in ("heading", "caption") else [b.text.strip()]):
            if s:
                units.append((i, s))
    return units


class PageCache:
    def __init__(self, db: Database, max_distance: int = 6):
        self.db = db
        self.max_distance = max_distance

    def lookup(self, h: str) -> PageContent | None:
        best = None
        for r in self.db.query("SELECT id, phash FROM pages"):
            d = hamming(h, r["phash"])
            if d <= self.max_distance and (best is None or d < best[0]):
                best = (d, r["id"])
        if not best:
            return None
        r = self.db.one("SELECT * FROM pages WHERE id=?", (best[1],))
        self.db.execute("UPDATE pages SET last_seen=?, seen_count=seen_count+1 WHERE id=?",
                        (_now(), best[1]))
        pc = PageContent.from_dict(json.loads(r["blocks_json"]))
        pc.page_id, pc.from_cache = r["id"], True
        return pc

    def store(self, h: str, page: PageContent, book: str = "My book") -> int:
        pid = self.db.execute(
            "INSERT INTO pages(phash,book,page_label,lang,confidence,blocks_json,first_seen,last_seen)"
            " VALUES(?,?,?,?,?,?,?,?)",
            (h, book, page.page_label, page.lang, page.confidence, page.to_json(), _now(), _now())).lastrowid
        page.page_id = pid
        return pid

    def _row(self, page_id: int) -> dict | None:
        return self.db.one("SELECT id, book, page_label FROM pages WHERE id=?", (page_id,))

    def successor(self, pages: "list[PageContent]") -> "list[PageContent] | None":
        """Predict the next spread from the cache: same book, printed labels last+1, last+2 (numeric), else the
        next sequential page ids. Returns cached pages (1-2) or None. Used to preload TTS before the flip."""
        last = pages[-1]
        row = self._row(last.page_id) if last.page_id else None
        if not row:
            return None
        found: list[PageContent] = []
        n = label_number(row["page_label"])
        if n is not None:
            for k in (1, 2):
                r = self.db.one("SELECT id FROM pages WHERE book IS ? AND page_label IN (?,?)", (row["book"], str(n + k), str(n + k)))
                if not r:
                    break
                found.append(self.get(r["id"]))
        else:
            rows = self.db.query("SELECT id FROM pages WHERE book IS ? AND id>? ORDER BY id LIMIT 2", (row["book"], row["id"]))
            if rows and rows[0]["id"] == row["id"] + 1:
                found = [self.get(r["id"]) for r in rows]
        return [p for p in found if p] or None

    def library(self) -> list[dict]:
        return self.db.query("SELECT id, book, page_label, lang, confidence, first_seen, seen_count FROM pages ORDER BY id")

    def get(self, page_id: int) -> PageContent | None:
        r = self.db.one("SELECT * FROM pages WHERE id=?", (page_id,))
        if not r:
            return None
        pc = PageContent.from_dict(json.loads(r["blocks_json"]))
        pc.page_id = page_id
        return pc


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
