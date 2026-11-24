#!/usr/bin/env bash
# Wait for the Kolektif realm to go live on onyx-1, then run the lifecycle.
#
# No LLM involved: it polls the chain directly and calls run_onyx.sh the moment
# the realm renders. Exits 0 with the tx output, or 1 if it never went live in
# the given window.
set -u
export PATH=$PATH:$HOME/gno-bin

MAX_MIN="${MAX_MIN:-120}"
RPC="${RPC:-https://rpc.onyx.testnets.gno.land:443}"
ADDR="${ADDR:-g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2}"
PKG="gno.land/r/$ADDR/kolektif"
LOG=/tmp/kolektif_wait.log
: > "$LOG"

deadline=$(( $(date +%s) + MAX_MIN * 60 ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  out=$(gnokey query vm/qrender -data "$PKG:" -remote "$RPC" 2>&1)
  if printf '%s' "$out" | grep -q "# Kolektif"; then
    echo "$(date -u +%H:%M:%S) REALM IS LIVE" | tee -a "$LOG"
    bash "$HOME/kolektif/demo/run_onyx.sh" 2>&1 | tee -a "$LOG"
    exit 0
  fi
  parked=$(gnokey query vm/qinertpaths -data "" -remote "$RPC" 2>/dev/null | grep -c "$ADDR")
  echo "$(date -u +%H:%M:%S) parked=$parked" >> "$LOG"
  sleep 60
done

echo "timeout after ${MAX_MIN}m; last state:" | tee -a "$LOG"
gnokey query vm/qinertpaths -data "" -remote "$RPC" 2>/dev/null | grep "$ADDR" | tee -a "$LOG"
exit 1
