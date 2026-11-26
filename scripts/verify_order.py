#!/usr/bin/env python3
"""Recompute a Kolektif payout order from the chain and compare it.

The realm prints a machine-readable proof on its party page:

    VERIFY v1
    circle=2
    height=1433732
    seed=2|1433732|g1aaa...,g1bbb...,g1ccc...
    sha256=<sha256 of seed>
    order=1,0,2

This script fetches that block over ABCI (no wallet, no RPC lib) and rebuilds
the order from the seed with the same Fisher-Yates + SHA-256(seed:counter)
stream the realm uses. It prints PASS when the realm's order is the one the
seed produces, and FAIL with both orders when it is not.

    python3 scripts/verify_order.py --rpc https://rpc.onyx.testnets.gno.land:443 --circle 2
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request

DEFAULT_PKG = "gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif"


def abci_query(rpc: str, path: str, data: str) -> str:
    import base64 as _b64
    # cometbft decodes params.data as base64, so the plain query string must be encoded
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "abci_query",
                       "params": {"path": path,
                                  "data": _b64.b64encode(data.encode()).decode()}}).encode()
    req = urllib.request.Request(rpc.rstrip("/"), data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())
    resp = payload["result"]["response"]
    raw = resp.get("ResponseBase", {}).get("Data")
    if not raw:
        raise SystemExit(f"no data for {path} {data!r}: {resp}")
    import base64
    return base64.b64decode(raw).decode(errors="replace")


def prng(seed: str):
    counter = 0
    buf = b""
    while True:
        while len(buf) < 8:
            buf += hashlib.sha256(f"{seed}:{counter}".encode()).digest()
            counter += 1
        chunk, buf = buf[:8], buf[8:]
        yield int.from_bytes(chunk, "big")


def order_for(n: int, seed: str) -> list[int]:
    idx = list(range(n))
    if n < 2:
        return idx
    stream = prng(seed)
    for i in range(n - 1, 0, -1):
        j = next(stream) % (i + 1)
        idx[i], idx[j] = idx[j], idx[i]
    return idx


def parse_proof(md: str) -> dict[str, str]:
    block = md[md.find("VERIFY v1"):] if "VERIFY v1" in md else ""
    out = {}
    for line in block.splitlines():
        m = re.match(r"^(circle|height|seed|sha256|order)=(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.onyx.testnets.gno.land:443")
    ap.add_argument("--pkg", default=DEFAULT_PKG)
    ap.add_argument("--circle", required=True, type=int)
    a = ap.parse_args()

    data = f"{a.pkg}:circle/{a.circle}/party"
    md = abci_query(a.rpc, "vm/qrender", data)
    proof = parse_proof(md)
    if "seed" not in proof or "order" not in proof:
        print("no VERIFY block found; is the circle activated?")
        return 2

    seed, claimed = proof["seed"], proof["order"]
    members = seed.split("|", 2)[2].split(",") if seed.count("|") >= 2 else []
    n = len(members)

    recomputed = ",".join(str(i) for i in order_for(n, seed))
    digest = hashlib.sha256(seed.encode()).hexdigest()

    print(f"circle     {a.circle}")
    print(f"height     {proof.get('height')}")
    print(f"members    {n}")
    print(f"seed       {seed}")
    print(f"sha256     {digest}  {'ok' if digest == proof.get('sha256') else 'MISMATCH'}")
    print(f"order page {claimed}")
    print(f"order calc {recomputed}")
    ok = claimed == recomputed and digest == proof.get("sha256")
    print("PASS: the order is exactly what the seed produces" if ok else "FAIL: the page does not match the seed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
