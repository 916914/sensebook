#!/usr/bin/env bash
# Pair + trust + connect Bluetooth earbuds (AirPods-class) with bluetoothctl, then make them the default sink.
# Usage: scripts/pair_bluetooth.sh            (scan 15 s, pick from the list)
#        scripts/pair_bluetooth.sh AA:BB:CC:DD:EE:FF
# Put the earbuds in pairing mode first (AirPods: hold the case button until the light flashes white).
set -euo pipefail

command -v bluetoothctl >/dev/null || { echo "bluetoothctl not found: sudo apt install bluez"; exit 1; }
sudo rfkill unblock bluetooth || true

MAC="${1:-}"
if [[ -z "$MAC" ]]; then
  echo "Scanning for 15 seconds..."
  bluetoothctl --timeout 15 scan on >/dev/null || true
  mapfile -t DEVS < <(bluetoothctl devices | sed 's/^Device //')
  [[ ${#DEVS[@]} -gt 0 ]] || { echo "No devices found."; exit 1; }
  for i in "${!DEVS[@]}"; do echo "  [$i] ${DEVS[$i]}"; done
  read -rp "Number to pair: " N
  MAC="${DEVS[$N]%% *}"
fi

echo "Pairing $MAC ..."
bluetoothctl pair "$MAC" || true      # already-paired is fine
bluetoothctl trust "$MAC"
bluetoothctl connect "$MAC"

# PipeWire (Bookworm default) exposes the earbuds as a bluez sink.
sleep 3
SINK=$(pactl list short sinks 2>/dev/null | awk '/bluez/ {print $2; exit}' || true)
if [[ -n "$SINK" ]]; then
  pactl set-default-sink "$SINK"
  echo "Default sink: $SINK"
  echo "Put this in config.yaml -> audio.bluetooth_sink: \"$SINK\" and set audio.output: bluetooth (or use the web app)."
else
  echo "Connected, but no bluez sink yet. Check: wpctl status | grep -i bluez"
fi
