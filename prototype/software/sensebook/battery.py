"""Optional MAX17048 fuel gauge (I2C 0x36 on GPIO 2/3) and the low-battery announcer."""
from __future__ import annotations


class Gauge:
    def percent(self) -> float | None: ...


class NullGauge(Gauge):
    def percent(self):
        return None


class FakeGauge(Gauge):
    """Tests and dev mode (`bat 18` on the console)."""

    def __init__(self, level: float | None = 80.0):
        self.level = level

    def percent(self):
        return self.level


class MAX17048Gauge(Gauge):
    ADDR, REG_SOC = 0x36, 0x04

    def __init__(self, bus: int = 1):
        from smbus2 import SMBus  # optional dependency (requirements-pi.txt)
        self.bus = SMBus(bus)
        self.bus.read_word_data(self.ADDR, self.REG_SOC)     # raises if the chip is not fitted

    def percent(self):
        try:
            w = self.bus.read_word_data(self.ADDR, self.REG_SOC)
        except OSError:
            return None
        return min(100.0, ((w & 0xFF) << 8 | w >> 8) / 256.0)      # SOC register is big-endian, 1/256 % units


def make_gauge(cfg: dict) -> Gauge:
    if cfg.get("gauge", "auto") == "none":
        return NullGauge()
    try:
        return MAX17048Gauge()
    except Exception:
        return NullGauge()


class BatteryMonitor:
    """poll() announces once per threshold crossing (20 %, 10 %) and re-arms after the level recovers above 25 %."""

    def __init__(self, gauge: Gauge, levels=(20, 10), announce=lambda pct, level: None, rearm_above: float = 25.0):
        self.gauge, self.levels, self.announce, self.rearm = gauge, sorted(levels, reverse=True), announce, rearm_above
        self.said: set[int] = set()
        self.last: float | None = None

    def poll(self) -> float | None:
        pct = self.gauge.percent()
        self.last = pct
        if pct is None:
            return None
        if pct > self.rearm:
            self.said.clear()
        for lv in self.levels:                      # most urgent crossed level wins, once
            if pct <= lv and lv not in self.said:
                self.said.update(l for l in self.levels if l >= lv)
                self.announce(pct, lv)
                break
        return pct

    @property
    def low(self) -> bool:
        return self.last is not None and self.last <= self.levels[0]
