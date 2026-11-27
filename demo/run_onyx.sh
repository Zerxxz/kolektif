#!/usr/bin/env bash
# Run the full Kolektif lifecycle on a live gno.land chain (onyx-1).
#
# Idempotent: if the realm already has circle #1 it does nothing, so it is safe
# to call from a monitor loop.
set -u
export PATH=$PATH:$HOME/gno-bin

RPC="${RPC:-https://rpc.onyx.testnets.gno.land:443}"
CHAIN="${CHAIN_ID:-onyx-1}"
ADDR="${ADDR:-g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2}"
PKG="gno.land/r/$ADDR/kolektif"
KEYS="${KEYS_HOME:-$HOME/.gno/onyx}"
PW="${GNO_PASSWORD:-$(cat "$HOME/.gno-key-pw")}"
GAS_FEE=1000000ugnot
GAS=25000000

say() { echo "[$(date -u +%H:%M:%S)] $*"; }

call() { # call <key> <func> [args...]
  local key="$1"; shift
  local fn="$1"; shift
  local args=()
  for a in "$@"; do args+=(-args "$a"); done
  local send=()
  if [ -n "${SEND:-}" ]; then send=(-send "$SEND"); fi
  printf '%s\n' "$PW" | gnokey maketx call \
    -pkgpath "$PKG" -func "$fn" "${args[@]}" "${send[@]}" \
    -gas-fee "$GAS_FEE" -gas-wanted "$GAS" \
    -chainid "$CHAIN" -remote "$RPC" \
    -home "$KEYS" -insecure-password-stdin -broadcast "$key" 2>&1 |
    grep -oE '"(PotPaid|CircleActivated|CircleClosed)"|TX HASH:.*'
}

say "checking $PKG"
if ! gnokey query vm/qrender -data "$PKG:" -remote "$RPC" >/tmp/onyx_render.txt 2>&1; then
  say "realm not live yet (still parked or not found)"; exit 2
fi
# the empty board also prints "Warung Crew" inside its gnokey hint, so gate on a
# rendered run card instead of the name
if grep -q "RUN #1" /tmp/onyx_render.txt; then
  say "circle already exists, nothing to do"; exit 0
fi
say "realm is LIVE — starting the lifecycle"

SEND=""; call alice Create "Warung Crew" 1000000 3 60
SEND="1000000ugnot"
for k in alice bob carol; do sleep 2; call "$k" Join 1; done

for round in 1 2 3; do
  say "round $round"
  for k in alice bob carol; do sleep 2; call "$k" Contribute 1; done
done

say "final render:"
gnokey query vm/qrender -data "$PKG:circle/1" -remote "$RPC" 2>&1 | tail -40
say "done"
