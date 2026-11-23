#!/usr/bin/env bash
# Assemble the final demo cut: title card, body, outro, per-action narration,
# captions burned on the FINAL timeline.
#
# Inputs: /tmp/kolektif_raw.mp4 (screen take) + /tmp/vo/*.mp3 (narration)
# Output: demo/demo-kolektif.mp4
set -eu

OUT="$(dirname "$0")/demo-kolektif.mp4"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
FONT_R=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
BODY_IN=6      # skip the pre-roll before the realm painted
BODY_LEN=44    # seconds of take kept
TITLE=3
OUTRO=3
TOTAL=$((TITLE + BODY_LEN + OUTRO))

ffmpeg -y -loglevel error \
  -f lavfi -i "color=c=0x0b0f14:s=1440x900:d=${TITLE}" \
  -i /tmp/kolektif_raw.mp4 \
  -f lavfi -i "color=c=0x0b0f14:s=1440x900:d=${OUTRO}" \
  -i /tmp/vo/01.mp3 -i /tmp/vo/03.mp3 -i /tmp/vo/02.mp3 -i /tmp/vo/04.mp3 \
  -filter_complex "\
[0:v]drawtext=fontfile=${FONT}:text='Kolektif':fontcolor=0x8ff0c0:fontsize=96:x=(w-tw)/2:y=330,\
drawtext=fontfile=${FONT_R}:text='Rotating savings circles, on gno.land':fontcolor=0xe8eef5:fontsize=38:x=(w-tw)/2:y=450,\
drawtext=fontfile=${FONT_R}:text='a realm that escrows the pot and renders its own UI':fontcolor=0x9aa7b4:fontsize=28:x=(w-tw)/2:y=510[t0];\
[1:v]trim=start=${BODY_IN}:duration=${BODY_LEN},setpts=PTS-STARTPTS,\
fade=t=in:st=0:d=0.7,fade=t=out:st=$((BODY_LEN-1)):d=1[body];\
[2:v]drawtext=fontfile=${FONT_R}:text='gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif':fontcolor=0x9aa7b4:fontsize=26:x=(w-tw)/2:y=430,\
drawtext=fontfile=${FONT_R}:text='MIT licensed  ·  Gnome Tavern 2026':fontcolor=0x6d7b8a:fontsize=22:x=(w-tw)/2:y=480[o0];\
[t0][body][o0]concat=n=3:v=1:a=0[base];\
[base]drawtext=fontfile=${FONT_R}:text='Rotating savings circles on chain — no bank, no treasurer':fontcolor=0xffffff:fontsize=30:box=1:boxcolor=0x000000@0.65:boxborderw=14:x=(w-tw)/2:y=h-120:enable='between(t,3.4,10.2)',\
drawtext=fontfile=${FONT_R}:text='Active circle: pot due this round, deadline, who has paid':fontcolor=0xffffff:fontsize=30:box=1:boxcolor=0x000000@0.65:boxborderw=14:x=(w-tw)/2:y=h-120:enable='between(t,11.0,24.0)',\
drawtext=fontfile=${FONT_R}:text='Only the group’s own money moves: collateral in, pot out':fontcolor=0xffffff:fontsize=30:box=1:boxcolor=0x000000@0.65:boxborderw=14:x=(w-tw)/2:y=h-120:enable='between(t,25.0,34.0)',\
drawtext=fontfile=${FONT_R}:text='Closed: 3 pots paid, collateral returned, realm balance 0':fontcolor=0xffffff:fontsize=30:box=1:boxcolor=0x000000@0.65:boxborderw=14:x=(w-tw)/2:y=h-120:enable='between(t,35.0,46.0)'[vout];\
[3:a]adelay=3300|3300[a1];\
[4:a]adelay=14000|14000[a2];\
[5:a]adelay=25500|25500[a3];\
[6:a]adelay=35500|35500[a4];\
[a1][a2][a3][a4]amix=inputs=4:normalize=0[mix];\
[mix]apad,atrim=0:${TOTAL},asetpts=PTS-STARTPTS[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 128k -movflags +faststart \
  "$OUT"

echo "--- probe ---"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of default=nw=1 "$OUT"
ls -lh "$OUT"
