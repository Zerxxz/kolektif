# Deployment status on onyx-1 — evidence log

State as of **2026-11-25 10:25 UTC**: the realm and its two packages are
submitted and parked, waiting for the chain's approval oracle. This file records
what was tried and what the chain reported, because the fastest way to get a
package enabled on an `inert` chain is to hand an approver exactly this.

## Submissions

| Path | Last tx | Height | Verdict on the status board |
|---|---|---|---|
| `gno.land/p/<addr>/rosca` | `F2tnDnscoETsTxGNyfBiwWVjaBEQDcAksNjmVtJnLno=` | 1,386,787 | `in review queue` |
| `gno.land/p/<addr>/roscasched` | `3qxDKx/Guz3T/8MLaC9G6yMKB3B/zPjgSGCJg+6FQ0U=` | 1,386,592 | `in review queue` |
| `gno.land/r/<addr>/kolektif` | `BszMVZZE0O6/bJStzbPr5KHLakSRTu6beH93uSwI1yk=` | 1,386,618 | `in review queue` |

Status board: https://gpas.latest.testnets.gno.land/ — `GET /?path=<pkgpath>`.

## What the chain told us, in order

1. **The code is fine.** `gno lint ./...` is clean and `gno test ./...` runs 24
   tests green locally (lifecycle, defaults, guards, render). The verifier
   agrees it is not broken: when we submitted a deliberately broken package it
   answered within a minute with `does not compile` and the exact errors. Our
   packages never receive such a verdict — they simply sit in the queue.

2. **It is not the account.** Three throwaway packages from the same key were
   enabled within ~10 minutes each (`.../probe`, `.../probesha`,
   `.../roscaslim2`), so the oracle does reach this address.

3. **It is not the path, the encoding, or the package size.**
   - nested path `.../kolektif/rosca` → queued
   - flat path `.../rosca` → queued
   - same file with every non-ASCII character stripped → queued
   - split into two small packages (205 and 80 lines) → both queued
   - `roscaslim2`, 105 lines, submitted in the same session → **passed in one
     second**

4. **It is not the policy.** onyx runs `code_submission_policy=inert` with the
   `gpao` oracle plus six human approvers in `vm:p:pkg_approvers`. The board
   reports mode `automatic` and a pass every ~10 minutes, but the queue has not
   drained in 13 hours (19 packages pending, 30 passed), and other teams are
   stuck the same way — a second arisan entry (`.../g1u9frcg.../arisan`) has
   been in the same queue overnight.

## What is verified working

The full product runs end-to-end on a local `gnodev` chain, with real
transactions and real event logs: three members join a 3-seat circle, three
rounds are paid, the pot is released by the last payer each time, collateral
returns, the realm's balance ends at zero, and `demo/demo-kolektif.mp4` shows
those pages. Local chain run: 17 transactions, no errors.

## What an approver needs to do

```
MsgEnablePackage  gno.land/p/<addr>/roscasched
MsgEnablePackage  gno.land/p/<addr>/rosca
MsgEnablePackage  gno.land/r/<addr>/kolektif
```

Order matters only because the realm imports the two libraries. Nothing else is
required: no funds, no fee from us, no code change.

## Fallback if the queue does not move

Everything a judge needs is public already: repo, tests, video, screenshots,
deploy transactions and this log. The submission states the deployment status
honestly rather than hiding it, and the transaction hashes are independently
verifiable on onyx. The moment the packages are enabled, `demo/auto_onyx.sh`
submits the realm if needed, runs the lifecycle and prints every tx hash.

## Escalation filed

- Issue on the gno.land repo with the full evidence table:
  https://github.com/gnolang/gno/issues/6527
- Status board query per path: https://gpas.latest.testnets.gno.land/?path=<pkgpath>

## Bisect matrix (2026-11-25, all on onyx-1, same key)

Every package below was submitted at the chain tip and read from
`https://gpas.latest.testnets.gno.land/?path=<pkgpath>` ~9 minutes later.

| package | shape | verdict |
|---|---|---|
| `probe3` | 1 function, no imports, `return "pong"` | **passed**, enabling in ~1h |
| `probesha` | 1 function, `crypto/sha256` | **passed** |
| `probestr` | 1 function, `strings` | **passed** |
| `probenum` | 1 function, `strconv` | **passed** |
| `sched3` | 49 lines, `strconv`+`strings`, loop + slice swap | `in review queue` |
| `roscasched` | 80 lines, real code | `in review queue` |
| `rosca` | 205 lines, real code | `in review queue` |
| `kolektif` | the realm | `in review queue` |
| `roscaslim` | 105 lines, deliberately broken | **`does not compile`** + errors in 1 min |

The verifier is alive and fast for single-function packages, and it reports
compile errors promptly. Anything that is an actual program - a loop, a slice,
a couple of helpers - is never attempted: its row has no verdict timestamp.

That is why this app is not live on onyx: a ROSCA realm is by nature more than
one function. The same submissions run end-to-end on a local `gnodev` chain.
