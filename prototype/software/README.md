# SenseBook prototype software

A screen-free AI study companion. A lamp-shaped device stands just beyond the top edge of an open printed book.
Its camera follows page turns, **reads the page aloud faithfully**, **explains and discusses** it in Bangla or
English, runs two-host **Chapter Talk** audio discussions you can interrupt, **tests** you with spoken quizzes
(spaced repetition), **remembers** what you learned (opt-in) and sets **reminders**. Everything works by audio and
buttons; a phone web app (PIN-protected) handles setup, memory and reminders.

Three run modes: `dev` (laptop: webcam, sounddevice, keyboard), `device` (Pi Zero 2 W: Picamera2 + M12 ultra-wide lens, I2S mics/amp/headphone DAC, gpiozero),
and the `mock` provider (offline, deterministic, no network, no key).

## Laptop quick start (Windows/macOS/Linux, Python 3.10+)

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1 ; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q               # offline tests

# offline demo, synthetic page-turning camera, silent output:
python -m sensebook --mode dev --provider mock --fake-camera --silent
# real Gemini + your webcam + speakers:
cp .env.example .env              # put GEMINI_API_KEY=... in .env (never commit it)
cp config.example.yaml config.yaml
python -m sensebook --mode dev --provider gemini
```
Companion app: http://127.0.0.1:8080 (dev mode binds to loopback only). First visit asks you to choose a guardian PIN.
Flags: `--no-camera`, `--fake-camera` (mock only), `--silent`, `--no-web`, `--config PATH`, `--purge-captures`.

### Keyboard map (dev mode)
Type the key then **Enter** (line-based, because held keys are unreliable in terminals; Ask is a toggle).

| Key | Action | Real button |
|---|---|---|
| `a` | Ask on / off (toggle record) | Ask (hold) |
| `p` | Play / Pause (also snoozes a reminder that just fired) | Play/Pause |
| `w` | "Where am I?": pages, sentence, battery | hold Play/Pause |
| `[` / `]` | Back / Forward one sentence (`[` twice quickly = previous paragraph; at the top of a spread: previous spread) | Back / Forward |
| `k` | Repeat the current sentence | hold Back |
| `+` / `-` | Volume | Vol+ / Vol- |
| `>` / `<` | Reading speed faster / slower | hold Vol+ / Vol- |
| `m` / `j` / `x` | Toggle mic-mute switch / headphone jack / hub attached-detached | switches |
| `bat 18` | Set the fake battery gauge to 18 % (announces at 20 % and 10 %) | MAX17048 |
| `t` / `d` / `r` / `q` | Test me / discussion / read page / quit | voice |
| `h` / `n` / `b` | `--fake-camera` demo: hand in/out, flip forward, flip back | |
| `say <text>` | Speak to the device without a mic (needed with the mock provider, which cannot hear audio) | |

"Forget everything" by voice is confirmed with **Forward** within 10 s (**Back** cancels).
Console lines like `[LED] capture ON`, `[amp] on`, `[haptic] attached` and `[light] 40%` stand in for the dots, amp enable, motor and light ring.

## Raspberry Pi Zero 2 W setup (step by step)

Hardware (final): Pi Zero 2 W, IMX708 (Camera Module 3 sensor) with an **M12 ultra-wide (~120 deg) lens** about 11 cm above the page,
tilted 23-26 deg from vertical, about 1 cm behind the top edge (needs the **Pi Zero 22-pin camera cable**); I2S MEMS mics,
MAX98357A speaker amp and an I2S headphone DAC on the one I2S bus; MAX17048 fuel gauge (optional); buttons, switches,
status dots, light ring, haptic motor and hub sensor wired per the pin map below. Not tested on hardware (see Verification).
The Waveshare WM8960 HAT remains a **legacy dev-kit** option (`audio.hat: wm8960`, see `docs/AUDIO.md`).

1. **Flash**: Raspberry Pi Imager -> *Raspberry Pi OS Lite (64-bit), Bookworm*. In the gear dialog set hostname, user `pi`,
   Wi-Fi, SSH. Boot, `ssh pi@sensebook.local`, `sudo apt update && sudo apt full-upgrade -y`.
2. **Swap** (512 MB RAM): `sudo dphys-swapfile swapoff; sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=512/' /etc/dphys-swapfile; sudo dphys-swapfile setup; sudo dphys-swapfile swapon`.
3. **Camera**: Bookworm auto-detects the IMX708 (`camera_auto_detect=1` in `/boot/firmware/config.txt`, the default).
   Check: `rpicam-hello --list-cameras`. If missing, add `dtoverlay=imx708` and reboot.
4. **apt packages**:
   ```bash
   sudo apt install -y python3-venv python3-picamera2 python3-opencv python3-numpy python3-lgpio \
        alsa-utils espeak-ng bluez pipewire-audio libspa-0.2-bluetooth pulseaudio-utils libportaudio2 git
   ```
5. **Audio (I2S)**: mics, amp and headphone DAC share one I2S bus (GPIO 18/19/20/21). Add the overlay to
   `/boot/firmware/config.txt`, create `/etc/asound.conf` and set the mixer: step by step in **`docs/AUDIO.md`**
   (device-tree overlay options, full duplex on one bus, MAX98357A enable pin, headphone jack detect). Afterwards `aplay -l`
   and `arecord -l` show the sound card. GPIO 2/3 (I2C, fuel gauge) and 18-21 (I2S) are not available for anything else.
   *Legacy WM8960 dev kit*: install the Waveshare driver instead, then set `audio.hat: wm8960`, `audio.alsa_device` and
   `audio.alsa_capture_device` to `plughw:wm8960soundcard`.
5b. **Lens calibration** (once per lens): `python scripts/calibrate_camera.py --images 'calib/*.jpg' --board 9x6 --square-mm 25 --model fisheye`
   writes the `camera.lens` block (model, K, D) into `config.yaml`. Without it the image is not undistorted (`model: none`).
6. **App + venv** (system site packages so the apt `picamera2`/`cv2`/`numpy` are visible):
   ```bash
   git clone <this repo> ~/sensebook && cd ~/sensebook/prototype/software   # or copy the folder
   python3 -m venv --system-site-packages .venv && . .venv/bin/activate
   pip install google-genai flask pyyaml python-dotenv sounddevice tzdata
   pip install -r requirements-pi.txt       # gpiozero (+ lgpio)
   cp .env.example .env && nano .env        # GEMINI_API_KEY
   cp config.example.yaml config.yaml
   ```
7. **Try it**: `python -m sensebook --mode device --provider gemini`. Open `http://sensebook.local:8080`, set the PIN.
   Device mode binds the web app to the LAN (0.0.0.0) behind the PIN; dev mode never does.
8. **systemd service**: `sudo cp deploy/sensebook.service /etc/systemd/system/` (edit paths/user), then
   `sudo usermod -aG audio,video,gpio,bluetooth pi && sudo loginctl enable-linger pi`,
   `sudo systemctl enable --now sensebook && journalctl -u sensebook -f`.
9. **Bluetooth earbuds**: `scripts/pair_bluetooth.sh` (pairs, trusts, connects, prints the sink name), then set
   Settings -> Audio output -> Bluetooth in the web app. See `docs/AUDIO.md`.

### Pin map (BCM, final)
| Function | GPIO | Function | GPIO |
|---|---|---|---|
| I2S BCLK / LRCLK | 18 / 19 | I2S DIN (mics) / DOUT (amp + DAC) | 20 / 21 |
| Ask (hold to talk) | 5 | Play/Pause (hold = where am I) | 6 |
| Back (hold = repeat) | 13 | Forward | 26 |
| Vol+ (hold = faster) | 23 | Vol- (hold = slower) | 24 |
| Mic-mute switch (low = muted) | 16 | Light ring (PWM) | 12 |
| Dot READY / LISTENING | 17 / 27 | Dot SENDING (capture) / BATTERY-WARN | 22 / 4 |
| Amp enable (MAX98357A SD) | 25 | Headphone jack detect | 7 |
| Haptic motor | 11 | Hub-attached sensor | 8 |
| I2C SDA / SCL (MAX17048, optional) | 2 / 3 | | |

Defined once in `sensebook/config.py`. The app alone owns GPIO 25 (`audio.amp_enable_owner: app`); the I2S overlay must have no shutdown-GPIO control (see `docs/AUDIO.md`). Behaviour: jack in -> switch to headphones, amp SD low, say "Headphones"; the amp is also off
after `audio.amp_idle_seconds` of silence. Hub attach -> "Attached" + buzz; detach while reading -> pause + "Detached".
Battery announced at 20 % and 10 %; included in "where am I?". Hub attach is followed by framing guidance ("Ready, I can see pages N and N+1",
"Book upside down", "Page edge not visible, move the book a little away"); low OCR confidence on an unseen page says
"For small print, pull the stick up", then waits for the view to change and settle (or, after `camera.small_print_wait_s` = 20 s, says "Press play when the stick is up" and waits for Play/Pause) before capturing at full resolution (`camera.full_res`).

## Seamless page flipping
Start reading once (Play); after that, turning the page needs no button.
- **Hand in frame** (skin-tone region or large motion blob entering from an edge): capture is paused and speech is stopped
  (`flip.hand_action: stop`, or `duck` to just lower the volume, `none`). A frame with a hand over the text is never captured:
  the high-res still is re-checked and discarded. Reading resumes when the scene has been still for `camera.stable_seconds` (0.6-1.0).
- **Auto-continue**: at the end of a spread a soft page-turn earcon plays (plus a spoken "turn the page" with *Accessibility mode*
  in the web app); when the new spread settles, reading starts at the top of its left page.
- **Preload**: while a spread is read, the first sentences of the predicted next spread (next printed page numbers, else next
  page ids, from the cache) are synthesized in the background. The log shows `[flip] settle->first audio N ms`; metrics are in `app.metrics["flip_to_audio"]`.
- **Back / skip**: flipping back says "Back to page N" and resumes at the last read sentence; skipping ahead says "Page N" (if the number was read).
  The Back button at the top of a spread returns to the unfinished sentence on the previous spread.
- **Mid-sentence flip**: `flip.stop_mode: immediate | word` (word = 0.25 s fade-out; TTS has no word timings).
- **Tilted camera** (above/behind the top edge, 30-35 deg): the page quadrilateral is found and keystone-corrected before splitting;
  otherwise the fixed `camera.homography` from config is used. Wide-lens barrel distortion is not corrected.
Try it: `python -m sensebook --mode dev --provider mock --fake-camera --silent`, then `r` (read) and `n` / `h` / `b`.

## Using it
Press Play to read the page. Hold Ask and talk: "explain this", "remind me to revise chapter 3 tomorrow at 7 pm",
"remember that the exam is on Friday", "test me", "discuss this chapter", "switch to English", "forget everything"
(deletion by voice needs Forward pressed within 10 s, Back cancels; deletion in the web app needs the PIN).
A chime plus a different voice always precedes AI explanations; the plain "reader voice" is only used for text printed on the page.
Memory is **off** until enabled in the web app. Offline: already-seen pages stay readable (offline voice: `espeak-ng` on the Pi, `pyttsx3` on laptops).

## Configuration and data
`config.yaml` (see `config.example.yaml`): model IDs, voices, thresholds, `webapp.host` (default `127.0.0.1`), pins are in code.
API key only in `.env` (git-ignored, redacted from errors). Data lives in `data/` (git-ignored): `sensebook.db` and,
only if `storage.keep_captures: true`, `data/captures/`. Purge captures: `python -m sensebook --purge-captures`.

## Verification status
- Verified here (offline): the pytest suite (see the test count in the last run); headless dev-mode smoke run with the mock provider and a synthetic camera.
- **Not verified**: any real Gemini call (no key in the build session: call shapes follow the Nov 2026 docs and are unexercised);
  Raspberry Pi hardware (Picamera2 + ultra-wide lens, I2S audio overlay, gpiozero on the real pins (tested only on gpiozero's mock pins), aplay/arecord, Bluetooth, MAX17048); the physical webcam path; real audio device I/O.

## Troubleshooting
- *"no webcam"*: another app holds it, or wrong `camera.device_index`; use `--no-camera` or `--fake-camera` (mock).
- *Curved/stretched page text*: calibrate the lens (step 5b); with `model: none` the ultra-wide distortion is not corrected.
- *Page never captured*: motion must exceed `camera.motion_threshold` then be still for `stable_seconds`; tune in config. Poor light -> "too dark" message; turn on the reading light.
- *"hold the book flatter"*: image blur/low confidence. Check camera focus (IMX708 autofocus needs >~10 cm; mounted at 38-40 cm is fine) and lighting.
- *No sound on Pi*: `aplay -l`, `speaker-test -c2`, check `/etc/asound.conf` and that GPIO 25 (amp SD) is high while playing (`pinctrl get 25`); see `docs/AUDIO.md`.
- *Bangla read by robot voice / garbled offline*: offline voices are a fallback only; `espeak-ng -v bn "..."` quality is limited.
- *Gemini errors*: key in `.env`? Model IDs in `config.yaml` current? `gemini.tts_api: generate_content` switches the TTS call shape.
- *Reminder did not fire*: the app must be running; overdue reminders fire at boot. Time zone is Asia/Dhaka.
- *Web app unreachable from phone*: only in `--mode device` (LAN); same Wi-Fi; port 8080.
