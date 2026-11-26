# Audio notes: I2S mics + MAX98357A + I2S headphone DAC (Pi Zero 2 W)

**Status: written from datasheets and upstream docs, NOT yet verified on the hardware.** Treat the overlay and
asound steps as a starting point for bench bring-up. The app is the only owner of GPIO 25 (amp enable) and GPIO 16 (mic-mute switch).

## Wiring (one I2S bus, full duplex)
| I2S line | GPIO | Connects to |
|---|---|---|
| BCLK | 18 | mics, MAX98357A, headphone DAC (shared) |
| LRCLK / WS | 19 | mics, MAX98357A, headphone DAC (shared) |
| DIN (data **into** the Pi) | 20 | I2S MEMS mics (SPH0645 / INMP441 class; SEL pins set left/right) |
| DOUT (data **out of** the Pi) | 21 | MAX98357A DIN **and** the headphone DAC (PCM5102-class) DIN |
| Amp enable | 25 | MAX98357A SD pin (low = amp off) |
| Jack detect | 7 | headphone jack switch (closes to GND when a plug is inserted) |

Two devices on DOUT is normal for I2S (listeners). Mic and DAC/amp share clocks, so capture and playback must run at the
same sample rate and format: use 48 kHz / 32-bit slots on the bus and let ALSA `plug` convert to 16 kHz S16 for the app.

## 1. Device-tree overlay (pick one)
**Option A (recommended): `googlevoicehat-soundcard`.** It is the stock overlay for "I2S mic + MAX98357A on one bus"
(full duplex, card name `sndrpigooglevoicehat`). In `/boot/firmware/config.txt`:
```
dtparam=audio=off
dtoverlay=googlevoicehat-soundcard
```
**The overlay must have NO shutdown-GPIO control.** The upstream overlay's codec node drives an amp-shutdown GPIO
(**GPIO 16 by default**). On SenseBook GPIO 16 is the mic-mute switch and GPIO 25 is the amp enable, and **the app is the
single owner of GPIO 25** (`audio.amp_enable_owner: app`, the default). So the kernel driver must touch neither pin. Use a
modified copy of the overlay:
```
git clone --depth 1 https://github.com/raspberrypi/linux && cd linux/arch/arm/boot/dts/overlays
cp googlevoicehat-soundcard-overlay.dts sensebook-i2s-overlay.dts
# remove the codec's  sdmode-gpios = <&gpio 16 0>;  line (the amp is controlled by the app, not the driver)
sed -i '/sdmode-gpios/d' sensebook-i2s-overlay.dts
dtc -@ -I dts -O dtb -o sensebook-i2s.dtbo sensebook-i2s-overlay.dts
sudo cp sensebook-i2s.dtbo /boot/firmware/overlays/      # then use  dtoverlay=sensebook-i2s  in config.txt
```
If the codec driver refuses to probe without a shutdown GPIO, point `sdmode-gpios` at a pin nothing else uses (GPIO 9 or 10;
**never 16, 25 or any pin in the README pin map**) and leave that pin unconnected.
Verify on the bench *before* running SenseBook (`sudo gpioinfo | grep -E "line +(16|25):"`, or `pinctrl get 16,25`):
both lines must show **no kernel consumer** (not `sdmode`/`voicehat`); GPIO 16 is a plain input and GPIO 25 is untouched until the
app starts and drives it. After starting the app, GPIO 25 must be high only while sound plays.

`audio.amp_enable_owner: driver` is the escape hatch for a build whose overlay owns the amp pin: the app then never claims
GPIO 25 (it only tracks the state in software), so "amp low when headphones are in" depends on the driver and the jack switch
(a physical break in the speaker path) and the idle power saving is lost. Not the supported configuration.

**Option B: separate playback/capture overlays.** `dtoverlay=hifiberry-dac` (playback on DOUT) plus a mic capture
card, combined in `/etc/asound.conf` as an `asym` device (see the Adafruit "I2S mic + amp on one Pi" guide). Some kernels
cannot open the two cards on one bus at the same time; if capture and playback clash, use Option A.

Reboot, then check: `aplay -l`, `arecord -l`, `dmesg | grep -i -E "i2s|voicehat|snd"`.

## 2. ALSA: `/etc/asound.conf`
```
pcm.!default { type asym playback.pcm "speaker_out" capture.pcm "mic_in" }

pcm.speaker_out { type plug slave.pcm "dmixed" }          # software mixing: chimes never block speech
pcm.dmixed { type dmix ipc_key 1024 slave { pcm "hw:sndrpigooglevoicehat" rate 48000 channels 2 format S32_LE } }

pcm.mic_raw { type plug slave { pcm "hw:sndrpigooglevoicehat" rate 48000 channels 2 format S32_LE } }
pcm.mic_in  { type softvol slave.pcm "mic_raw" control { name "Mic Gain" card sndrpigooglevoicehat } min_dB -10.0 max_dB 30.0 }
ctl.!default { type hw card sndrpigooglevoicehat }
```
The app plays to `audio.alsa_device` (`default`) and records from `audio.alsa_capture_device` (`mic_in`), mono 16 kHz S16
(`arecord -D mic_in -f S16_LE -r 16000 -c 1`). I2S MEMS mics are quiet: raise the `Mic Gain` softvol
(`amixer -c sndrpigooglevoicehat sset 'Mic Gain' 70%`) until speech peaks around -12 dBFS. Persist with `sudo alsactl store`.
Test: `speaker-test -D default -c2 -t sine -f 440`, `arecord -D mic_in -f S16_LE -r 16000 -c 1 -d 5 t.wav && aplay t.wav`.

## 3. Speaker vs headphones (no mixer involved)
The MAX98357A and the headphone DAC hear the same DOUT stream. Routing is the amp's SD pin:
* speaker mode (`amp_enable_owner: app`): GPIO 25 high only while sound plays (SenseBook raises it before playback, ~20 ms turn-on, and drops it
  `audio.amp_idle_seconds` after the last sound to save power);
* jack inserted (GPIO 7): SenseBook says "Headphones", holds GPIO 25 low and routes nothing to the speaker; unplugging says "Speaker";
* the jack switch should also physically open the speaker path if you want a hardware guarantee.
Private mode (default on) means a non-speaker output always keeps the amp off.

## 4. Bluetooth earbuds (PipeWire, Bookworm default)
```
sudo apt install bluez pipewire-audio libspa-0.2-bluetooth pulseaudio-utils
scripts/pair_bluetooth.sh          # pair + trust + connect, prints the sink name
wpctl status | grep -i bluez       # sink should appear
```
Set `audio.bluetooth_sink` and choose Bluetooth in the web app. SenseBook then plays to ALSA `default` routed by PipeWire
(install `pipewire-alsa` so `default` goes through it), and the amp is held off. A2DP is output only; the on-board mics
stay the input. Run the service as the login user (`loginctl enable-linger pi`) so the user PipeWire session exists at boot.
If the earbuds are not connected the router falls back to the speaker rather than staying silent.

## 5. Legacy: Waveshare WM8960 dev kit
Still supported for bench work on a laptop-like setup: install the Waveshare driver (`WM8960-Audio-HAT` install script), then
```
audio:
  hat: wm8960
  alsa_device: plughw:wm8960soundcard
  alsa_capture_device: plughw:wm8960soundcard
  mixer_card: wm8960soundcard
```
With `hat: wm8960` routing uses `amixer` (`Speaker`, `Headphone`; levels via `Playback`, `Capture`; `alsactl store`), and the
amp-enable GPIO is irrelevant. The WM8960 HAT uses the same GPIO 18-21 / 2-3, so it cannot be combined with the final I2S parts.
