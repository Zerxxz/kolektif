#!/usr/bin/env bash
# Record a cursor-driven demo of the Kolektif realm on a local gnodev chain.
#
# Produces /tmp/kolektif_raw.mp4 plus /tmp/kolektif_timeline.json (measured
# action seconds for narration and captions).
set -u
export PATH=$PATH:$HOME/gno-bin
export GNOROOT=$HOME/gno-src
ADDR=g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2
URL="http://127.0.0.1:8888/r/$ADDR/kolektif"
KEYS=$HOME/.gno/demo

echo "== 1. seed demo state =="
( cd "$(dirname "$0")/.." && ./demo/run_demo.sh >/tmp/demo_seed.log 2>&1 ) || true
grep -c "TX HASH" /tmp/demo_seed.log || true

echo "== 2. wait for the realm to actually render =="
for i in $(seq 1 60); do
  if curl -s -m 5 "$URL" | grep -q "Kolektif"; then
    echo "realm ready after ${i}s"; break
  fi
  sleep 1
done
curl -s -m 5 "$URL" | grep -q "Kolektif" || { echo "realm never rendered"; exit 1; }

echo "== 2b. clean stale display/profile =="
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
rm -rf /tmp/kolektif-profile /tmp/kolektif_raw.mp4
pkill -f 'Xvfb :9[9]' 2>/dev/null || true
sleep 1

echo "== 3. virtual display =="
Xvfb :99 -screen 0 1440x900x24 >/tmp/xvfb.log 2>&1 &
sleep 2

echo "== 4. chrome =="
DISPLAY=:99 google-chrome \
  --user-data-dir=/tmp/kolektif-profile \
  --no-first-run --no-default-browser-check --disable-infobars \
  --disable-gpu --no-sandbox --no-zygote --disable-dev-shm-usage \
  --window-size=1440,900 --window-position=0,0 \
  --remote-debugging-port=9222 --remote-allow-origins=* \
  --app="$URL" >/tmp/chrome.log 2>&1 &
sleep 8

echo "== 5. record =="
ffmpeg -y -loglevel error -f x11grab -framerate 12 -video_size 1440x900 \
  -draw_mouse 1 -i :99 -c:v libx264 -preset ultrafast -pix_fmt yuv420p \
  -crf 22 /tmp/kolektif_raw.mp4 >/tmp/ffmpeg.log 2>&1 &
FFPID=$!
sleep 2

echo "== 6. drive the UI =="
"$HOME/venv_new/bin/python3" "$(dirname "$0")/record_demo.py" 2>&1 | tail -30

sleep 1
kill -INT $FFPID 2>/dev/null
wait $FFPID 2>/dev/null
echo "== 7. raw take =="
ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/kolektif_raw.mp4

# stop chrome / display so the box is free for the encode
pkill -f 'kolektif-profil[e]' 2>/dev/null || true
pkill -f 'Xvfb :9[9]' 2>/dev/null || true
echo "== done =="
