"""Optional local-only store for page images / Ask audio. Off by default; purgeable."""
from __future__ import annotations

import time
from pathlib import Path


class CaptureStore:
    def __init__(self, cfg: dict):
        self.enabled = bool(cfg.get("storage", {}).get("keep_captures"))
        self.dir = Path(cfg["data_dir"]) / "captures"

    def save(self, kind: str, data: bytes, ext: str) -> Path | None:
        if not self.enabled or not data:
            return None
        self.dir.mkdir(parents=True, exist_ok=True)
        p = self.dir / f"{kind}-{int(time.time() * 1000)}.{ext}"
        p.write_bytes(data)
        return p

    def purge(self) -> int:
        n = 0
        if self.dir.exists():
            for f in self.dir.rglob("*"):
                if f.is_file():
                    f.unlink()
                    n += 1
        return n
