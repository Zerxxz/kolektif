#!/usr/bin/env bash
# Unattended chain to a live Kolektif on onyx-1.
#
#   1. wait until both library packages are live
#   2. submit the realm fresh (its earlier submissions were made while the
#      imports were still parked, so the verifier could not resolve them)
#   3. wait for the realm to render, then run the full lifecycle
#
# Every step is idempotent and safe to re-run.
set -u
export PATH=$PATH:$HOME/gno-bin

RPC="${RPC:-https://rpc.onyx.testnets.gno.land:443}"
ADDR="${ADDR:-g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2}"
KEYS="${KEYS_HOME:-$HOME/.gno/onyx}"
PW="${GNO_PASSWORD:-$(cat "$HOME/.gno-key-pw")}"
REPO="$HOME/kolektif"
MAX_MIN="${MAX_MIN:-720}"
LOG=/tmp/kolektif_auto.log

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

live() { # live <pkgpath>
  gnokey query vm/qfile -data "$1" -remote "$RPC" 2>&1 | grep -q "^data:" && return 0
  return 1
}

submit_realm() {
  log "submitting realm"
  printf '%s\n' "$PW" | gnokey maketx addpkg \
    -pkgpath "gno.land/r/$ADDR/kolektif" \
    -pkgdir "$REPO/gno.land/r/$ADDR/kolektif" \
    -gas-fee 3000000ugnot -gas-wanted 200000000 \
    -chainid onyx-1 -remote "$RPC" -home "$KEYS" \
    -insecure-password-stdin -broadcast chime 2>&1 |
    grep -E "TX HASH|HEIGHT|Error" | head -3 | tee -a "$LOG"
}

deadline=$(( $(date +%s) + MAX_MIN * 60 ))
realm_submitted=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  r_ok=0; s_ok=0
  live "gno.land/p/$ADDR/rosca" && r_ok=1
  live "gno.land/p/$ADDR/roscasched" && s_ok=1

  if [ "$r_ok" = 1 ] && [ "$s_ok" = 1 ] && [ "$realm_submitted" = 0 ]; then
    log "libraries are live"
    submit_realm
    realm_submitted=1
  fi

  if gnokey query vm/qrender -data "gno.land/r/$ADDR/kolektif:" -remote "$RPC" 2>&1 | grep -q "# Kolektif"; then
    log "REALM IS LIVE - running lifecycle"
    bash "$REPO/demo/run_onyx.sh" 2>&1 | tee -a "$LOG"
    exit 0
  fi

  log "waiting: rosca=$r_ok roscasched=$s_ok realm_submitted=$realm_submitted"
  sleep 120
done
log "timeout"
exit 1
