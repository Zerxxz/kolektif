#!/usr/bin/env bash
# Demo driver for Kolektif on a local gnodev chain.
#
# Prereq: gnodev running with three premined accounts (alice, bob, carol) in
# the keybase, e.g.
#
#   gnodev . -home ~/.gno/demo \
#     -add-account alice=5000000000ugnot \
#     -add-account bob=5000000000ugnot \
#     -add-account carol=5000000000ugnot
#
# Usage: ./demo/run_demo.sh /path/to/kolektif
set -u

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
ADDR="g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2"
PKG="gno.land/r/$ADDR/kolektif"
HOME_KEYS="${GNOKEY_HOME:-$HOME/.gno/demo}"
PW="${DEMO_PASSWORD:-$(cat "$HOME_KEYS/.pw")}"
RPC="${RPC:-tcp://127.0.0.1:26657}"
CHAIN="${CHAIN_ID:-dev}"
GAS_FEE="${GAS_FEE:-1000000ugnot}"
GAS="${GAS:-20000000}"

call () { # call <key> <func> [args...]
  local key="$1"; shift
  local fn="$1"; shift
  local args=()
  for a in "$@"; do args+=(-args "$a"); done
  local send=()
  if [ -n "$SEND" ]; then send=(-send "$SEND"); fi
  printf '%s\n' "$PW" | gnokey maketx call \
    -pkgpath "$PKG" -func "$fn" "${args[@]}" "${send[@]}" \
    -gas-fee "$GAS_FEE" -gas-wanted "$GAS" \
    -chainid "$CHAIN" -remote "$RPC" \
    -home "$HOME_KEYS" -insecure-password-stdin -broadcast "$key" 2>&1 |
    grep -oE '"(PotPaid|CircleActivated|CircleClosed|DefaultsDeclared)"|TX HASH:.*' | head -2
}

SEND="1000000ugnot"                      # 1 GNOT: collateral and round payment
CONTRIB=1000000                          # 1 GNOT in ugnot

echo "== circle 1: 3 members, 1 GNOT per round, 60s rounds =="
SEND=""
call alice Create 'Warung Crew' "$CONTRIB" 3 60
SEND="1000000ugnot"
for k in alice bob carol; do call "$k" Join 1; done

echo "== three rounds: the last payer releases the pot =="
for round in 1 2 3; do
  echo "-- round $round"
  for k in alice bob carol; do call "$k" Contribute 1; done
done

echo "== circle 2: a second circle, left mid-round =="
SEND=""
call bob Create 'Kampung Kopi' "$CONTRIB" 3 600
SEND="1000000ugnot"
for k in alice bob carol; do call "$k" Join 2; done
call alice Contribute 2

echo "== done: http://127.0.0.1:8888/r/$ADDR/kolektif =="
