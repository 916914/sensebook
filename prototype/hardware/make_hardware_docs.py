"""Draw the wiring diagram and write the pin map, straight from the software's pin table.

The pins are imported from prototype/software/sensebook/config.py (PINS, I2S_PINS, I2C_PINS), the same
table hardware.py uses, so this document cannot drift from the code. Run from the repo root:

    design\\.venv\\Scripts\\python.exe prototype\\hardware\\make_hardware_docs.py

Writes prototype/hardware/wiring_diagram.png, wiring_diagram.svg and pinmap.md.
Not yet verified on hardware: this is the intended wiring for the first bench build.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "software"))
from sensebook.config import I2C_PINS, I2S_PINS, PINS  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

# 40-pin header: physical pin -> name
HEADER = {1: "3V3", 2: "5V", 3: "GPIO2", 4: "5V", 5: "GPIO3", 6: "GND", 7: "GPIO4", 8: "GPIO14", 9: "GND", 10: "GPIO15",
          11: "GPIO17", 12: "GPIO18", 13: "GPIO27", 14: "GND", 15: "GPIO22", 16: "GPIO23", 17: "3V3", 18: "GPIO24",
          19: "GPIO10", 20: "GND", 21: "GPIO9", 22: "GPIO25", 23: "GPIO11", 24: "GPIO8", 25: "GND", 26: "GPIO7",
          27: "ID_SD", 28: "ID_SC", 29: "GPIO5", 30: "GND", 31: "GPIO6", 32: "GPIO12", 33: "GPIO13", 34: "GND",
          35: "GPIO19", 36: "GPIO16", 37: "GPIO26", 38: "GPIO20", 39: "GND", 40: "GPIO21"}
BCM2PIN = {int(v[4:]): k for k, v in HEADER.items() if v.startswith("GPIO")}

ROLE = {  # function key -> (what it is, how it is wired)
    "ask": ("Ask button (hold to talk)", "switch to GND, internal pull-up"),
    "play_pause": ("Play / Pause (hold = where am I)", "switch to GND, internal pull-up"),
    "back": ("Back (hold = repeat)", "switch to GND, internal pull-up"),
    "forward": ("Forward", "switch to GND, internal pull-up"),
    "vol_up": ("Volume + (hold = faster)", "switch to GND, internal pull-up"),
    "vol_down": ("Volume - (hold = slower)", "switch to GND, internal pull-up"),
    "mic_mute": ("Mic-mute slide switch", "closed to GND = muted, internal pull-up"),
    "dot_ready": ("Status dot: ready", "LED + 330 ohm to GND"),
    "dot_listening": ("Status dot: listening", "LED + 330 ohm to GND"),
    "dot_sending": ("Status dot: sending (capture)", "LED + 330 ohm to GND"),
    "dot_warn": ("Status dot: battery / warning", "LED + 330 ohm to GND"),
    "light": ("Light ring, PWM", "gate of an N-MOSFET (AO3400-class), 100 ohm in series, 100 k to GND"),
    "amp_enable": ("Amp enable (MAX98357A SD)", "direct; low = amp off"),
    "jack_detect": ("Headphone jack detect", "jack switch to GND when a plug is in, internal pull-up"),
    "haptic": ("Vibration motor", "base of an NPN (or MOSFET gate) with 1 k, flyback diode across the motor"),
    "hub_attached": ("Hub sensor", "detector switch to GND when the rear leg is deployed, internal pull-up"),
}
COL = dict(power="#B03A2E", gnd="#3B4448", i2s="#1F6F78", i2c="#C98A1B", gpio="#2E4A52", led="#7D6608", box="#F4F6F5",
           ink="#1D2A2E", line="#B8C4C6")


def pin_of(key):
    return BCM2PIN[PINS[key]]


def pinmap_md():
    rows = []
    for key, bcm in sorted(PINS.items(), key=lambda kv: BCM2PIN[kv[1]]):
        rows.append((BCM2PIN[bcm], bcm, ROLE[key][0], ROLE[key][1], f"`{key}`"))
    for name, bcm, what, how in (("bclk", I2S_PINS["bclk"], "I2S bit clock", "to both mics, MAX98357A BCLK, DAC BCK"),
                                 ("lrclk", I2S_PINS["lrclk"], "I2S word select (LRCLK)", "to both mics WS, MAX98357A LRC, DAC LCK"),
                                 ("din", I2S_PINS["din"], "I2S data into the Pi", "from both mics SD (one L, one R)"),
                                 ("dout", I2S_PINS["dout"], "I2S data out of the Pi", "to MAX98357A DIN and DAC DIN"),
                                 ("sda", I2C_PINS["sda"], "I2C data", "MAX17048 SDA (address 0x36), optional"),
                                 ("scl", I2C_PINS["scl"], "I2C clock", "MAX17048 SCL, optional")):
        rows.append((BCM2PIN[bcm], bcm, what, how, f"`{name}`"))
    rows.sort()
    out = ["# SenseBook prototype: pin map", "",
           "> **Generated** by `make_hardware_docs.py` from `prototype/software/sensebook/config.py`, the table that "
           "`hardware.py` uses. Do not edit by hand: change `config.py` and run the script again.",
           "> **Status:** intended wiring for the first bench build. Not yet verified on hardware.", "",
           "Board: Raspberry Pi Zero 2 W, 40-pin header (solder wires to the pads; no pin header fits in the unit). "
           "All logic is 3.3 V. BCM = the GPIO number used in the code.", "",
           "| Header pin | BCM GPIO | Function | Wiring | Key in `config.py` |", "|---|---|---|---|---|"]
    for pin, bcm, what, how, key in rows:
        out.append(f"| {pin} | {bcm} | {what} | {how} | {key} |")
    out += ["", "## Power and ground", "",
            "| Header pin | Net | Goes to |", "|---|---|---|",
            "| 2, 4 | 5 V | 5 V out of the charger + boost board (the only supply into the Pi) |",
            "| 1, 17 | 3.3 V (from the Pi) | I2S mics, headphone DAC logic, MAX17048 pull-ups; about 50 mA spare in total (EST) |",
            "| 6, 9, 14, 20, 25, 30, 34, 39 | GND | common ground: boost board, audio boards, every switch and LED |",
            "", "The MAX98357A is powered from 5 V (boost output), not from the Pi's 3.3 V pin. The light ring and the "
            "vibration motor also take their current from 5 V or the battery through their transistors, never from a GPIO pin.",
            "", "## Camera", "",
            "22-pin 0.5 mm CSI connector on the Pi Zero 2 W to the camera board (15-pin 1 mm on a Camera Module 3 form "
            "factor), using the Pi Zero camera cable.",
            "", "## Things to watch on the bench", "",
            "- **GPIO 4** (battery / warning dot) has a pull-up at boot. The LED may glow faintly until the app starts. "
            "If it does, move the resistor to 1 k or add a 10 k pull-down.",
            "- **GPIO 7 and 8** are the SPI chip-select pins and **GPIO 11** is SPI clock. Keep SPI off "
            "(`dtparam=spi=off`, the default) or these inputs and the motor pin will be driven by the kernel.",
            "- **GPIO 12** is PWM0, also used by the Pi's analogue audio. `dtparam=audio=off` is required (it is in the audio set-up).",
            "- **GPIO 16** is the default shutdown pin of the `googlevoicehat-soundcard` overlay. Use the modified overlay "
            "from `prototype/software/docs/AUDIO.md`, or the mic-mute switch will fight the sound driver.",
            "- **GPIO 2 and 3** have fixed 1.8 k pull-ups on the board: do not add more on the fuel-gauge breakout.",
            "- The I2S clock lines go to four devices. Keep those wires short (under 8 cm) and twist each with a ground wire.",
            "", "![Wiring diagram](wiring_diagram.png)", ""]
    with open(os.path.join(HERE, "pinmap.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))


def diagram():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5})
    fig, ax = plt.subplots(figsize=(17, 11.4), dpi=170)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 11.4)
    ax.axis("off")
    X0, X1, YT, DY = 8.05, 8.95, 10.0, 0.445

    def pxy(pin):
        row = (pin - 1) // 2
        return (X0 if pin % 2 else X1), YT - row * DY

    # Pi board and header
    ax.add_patch(FancyBboxPatch((7.2, YT - 19 * DY - 0.75), 2.6, 19 * DY + 1.5, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#E6F0EA", ec="#0E5C33", lw=1.6))
    ax.text(8.5, YT + 0.52, "Raspberry Pi Zero 2 W", ha="center", fontsize=11, fontweight="bold", color="#0E5C33")
    ax.text(8.5, YT + 0.30, "40-pin header (pad number / BCM name)", ha="center", fontsize=7.5, color=COL["ink"])
    for pin, name in HEADER.items():
        x, y = pxy(pin)
        c = COL["power"] if name in ("5V", "3V3") else COL["gnd"] if name == "GND" else "#C9A227"
        ax.add_patch(Rectangle((x - 0.085, y - 0.085), 0.17, 0.17, fc=c, ec=COL["ink"], lw=0.5))
        ax.text(x + (-0.16 if pin % 2 else 0.16), y, f"{pin}", ha="right" if pin % 2 else "left", va="center", fontsize=6.5,
                color=COL["ink"])
        ax.text(8.5 + (-0.08 if pin % 2 else 0.08), y, name.replace("GPIO", "G"), ha="right" if pin % 2 else "left", va="center",
                fontsize=6.2, color="#44555A")
    ax.text(8.5, YT - 19 * DY - 0.5, "CSI camera connector (22-pin flex)", ha="center", fontsize=7.5, color=COL["ink"])

    def box(x, y, w, h, title, lines=(), fc=COL["box"]):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=COL["ink"], lw=1.0))
        ax.text(x + 0.1, y + h - 0.17, title, fontsize=8.6, fontweight="bold", color=COL["ink"], va="center")
        for i, t in enumerate(lines):
            ax.text(x + 0.1, y + h - 0.42 - 0.2 * i, t, fontsize=7.0, color="#3B4A4F", va="center")

    chan = {"L": 0, "R": 0}

    def wire(pin, x_end, y_end, color, label=None, lw=1.3):
        x, y = pxy(pin)
        side = "L" if pin % 2 else "R"
        k = chan[side]
        chan[side] += 1
        xc = (7.05 - 0.085 * k) if side == "L" else (9.95 + 0.085 * k)
        ax.plot([x, xc, xc, x_end], [y, y, y_end, y_end], color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round")
        if label:
            ax.text(x_end + (0.06 if side == "L" else -0.06), y_end + 0.075, label, fontsize=6.6, color=color,
                    ha="left" if side == "L" else "right", va="bottom")

    L, R = 4.55, 12.45          # block edges that face the Pi
    # ---------------- left side (odd pins)
    box(0.5, 9.25, 4.05, 1.2, "MAX17048 fuel gauge (optional)", ["I2C address 0x36; VIN to the cell +, GND", "3V3 logic from header pin 1"])
    wire(1, L, 10.20, COL["power"], "3V3")
    wire(3, L, 9.90, COL["i2c"], f"SDA  GPIO {I2C_PINS['sda']}")
    wire(5, L, 9.60, COL["i2c"], f"SCL  GPIO {I2C_PINS['scl']}")
    box(0.5, 6.95, 4.05, 1.95, "Status dots: 4 white LEDs", ["each: GPIO -> 330 ohm -> LED -> GND", "about 4 mA per dot"])
    for i, key in enumerate(("dot_warn", "dot_ready", "dot_listening", "dot_sending")):
        wire(pin_of(key), L, 8.55 - 0.42 * i, COL["led"], f"{ROLE[key][0].split(': ')[1]}  GPIO {PINS[key]}")
    box(0.5, 5.5, 4.05, 1.1, "Vibration motor (10 mm coin)", ["GPIO -> 1 k -> NPN base; motor from 3V3/5 V;", "1N4148 diode across the motor"])
    wire(pin_of("haptic"), L, 6.05, COL["gpio"], f"haptic  GPIO {PINS['haptic']}")
    box(0.5, 2.55, 4.05, 2.6, "Top buttons (tact switches)", ["each: GPIO -> switch -> GND", "pull-ups are inside the Pi (gpiozero)"])
    for i, key in enumerate(("ask", "play_pause", "back", "forward")):
        wire(pin_of(key), L, 4.55 - 0.5 * i, COL["gpio"], f"{ROLE[key][0].split(' (')[0]}  GPIO {PINS[key]}")
    box(0.5, 0.55, 4.05, 1.6, "Camera", ["12 MP IMX708 board with M12 holder", "ultra-wide lens (~120 deg), 22-pin flex", "to the Pi's CSI connector"])
    ax.plot([4.55, 6.3, 6.3, 7.9], [1.3, 1.3, 0.95, 0.95], color="#8E6C1F", lw=3.0, solid_capstyle="round")
    ax.text(5.0, 1.38, "CSI flex", fontsize=6.6, color="#8E6C1F")

    # ---------------- right side (even pins)
    box(12.45, 9.05, 4.05, 1.4, "Power: charger + 5 V boost (USB-C)", ["2 x 102535 LiPo in parallel, each with protection",
                                                                   "BAT+ / BAT- in, 5 V out; slide switch in BAT+",
                                                                   "5 V also feeds the amp, light ring and motor"], fc="#FBEFEA")
    wire(2, R, 10.15, COL["power"], "5 V")
    wire(4, R, 9.90, COL["power"], "5 V")
    wire(6, R, 9.60, COL["gnd"], "GND (common)")
    box(12.45, 6.55, 4.05, 2.15, "Audio: one I2S bus", ["MAX98357A amp -> speaker 8 ohm 1 W (VIN 5 V)",
                                                     "PCM5102-class DAC -> 3.5 mm jack (line out)",
                                                     "2 x I2S MEMS mics (L/R select tied low / high)",
                                                     "BCLK and LRCLK go to all four devices"], fc="#E8F2F3")
    wire(12, R, 8.40, COL["i2s"], f"BCLK  GPIO {I2S_PINS['bclk']}")
    wire(pin_of("amp_enable"), R, 7.35, COL["gpio"], f"amp SD  GPIO {PINS['amp_enable']}")
    wire(38, R, 6.95, COL["i2s"], f"mics -> DIN  GPIO {I2S_PINS['din']}")
    wire(40, R, 6.70, COL["i2s"], f"DOUT -> amp + DAC  GPIO {I2S_PINS['dout']}")
    # LRCLK is on an odd pin: take it under the header to the audio block
    x35, y35 = pxy(35)
    ax.plot([x35, 6.2, 6.2, 11.6, 11.6, R], [y35, y35, 0.42, 0.42, 7.95, 7.95], color=COL["i2s"], lw=1.3)
    ax.text(R - 0.06, 8.02, f"LRCLK  GPIO {I2S_PINS['lrclk']} (header pin 35)", fontsize=6.6, color=COL["i2s"], ha="right", va="bottom")
    box(12.45, 5.1, 4.05, 1.1, "Side buttons", ["Volume + and Volume - : GPIO -> switch -> GND"])
    wire(pin_of("vol_up"), R, 5.80, COL["gpio"], f"Vol+  GPIO {PINS['vol_up']}")
    wire(pin_of("vol_down"), R, 5.45, COL["gpio"], f"Vol-  GPIO {PINS['vol_down']}")
    box(12.45, 3.2, 4.05, 1.55, "Switches and sensors", ["hub sensor: closed to GND = rear leg deployed",
                                                       "jack detect: closed to GND = plug in",
                                                       "mic mute: closed to GND = muted"])
    wire(pin_of("hub_attached"), R, 4.40, COL["gpio"], f"hub sensor  GPIO {PINS['hub_attached']}")
    wire(pin_of("jack_detect"), R, 4.00, COL["gpio"], f"jack detect  GPIO {PINS['jack_detect']}")
    wire(pin_of("mic_mute"), R, 3.45, COL["gpio"], f"mic mute  GPIO {PINS['mic_mute']}")
    box(12.45, 1.45, 4.05, 1.4, "Light ring: 8 warm-white LEDs", ["GPIO -> 100 ohm -> N-MOSFET gate (100 k to GND)",
                                                                "LEDs + resistors from 5 V, switched to GND",
                                                                "about 1 to 1.5 W at full brightness (EST)"], fc="#FCF6E3")
    wire(pin_of("light"), R, 2.15, COL["led"], f"light PWM  GPIO {PINS['light']}")

    # legend and title
    ax.text(0.5, 11.05, "SenseBook prototype: wiring diagram", fontsize=15, fontweight="bold", color=COL["ink"])
    ax.text(0.5, 10.78, "Drawn from prototype/software/sensebook/config.py. Intended wiring, not yet verified on hardware. "
                        "All logic 3.3 V.", fontsize=8.5, color="#44555A")
    lx = 12.5
    for i, (k, t) in enumerate((("power", "power"), ("gnd", "ground"), ("i2s", "I2S audio bus"), ("i2c", "I2C"),
                                ("gpio", "buttons, switches, control"), ("led", "LED drive"))):
        ax.plot([lx, lx + 0.35], [0.95 - 0.16 * i, 0.95 - 0.16 * i], color=COL[k], lw=2.2)
        ax.text(lx + 0.45, 0.95 - 0.16 * i, t, fontsize=7.2, va="center", color=COL["ink"])
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
    fig.savefig(os.path.join(HERE, "wiring_diagram.png"))
    fig.savefig(os.path.join(HERE, "wiring_diagram.svg"))
    plt.close(fig)


if __name__ == "__main__":
    assert len(set(PINS.values())) == len(PINS), "duplicate GPIO in config.PINS"
    pinmap_md()
    diagram()
    print("pin map and wiring diagram written for", len(PINS), "GPIO functions")
