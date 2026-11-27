# DoraHacks submission — paste-ready

Event: **Gnome Tavern Hackathon** · https://dorahacks.io/hackathon/gnome-tavern/detail
Deadline: **2026-12-18 01:00 UTC** · Prize: $20,000 in GNOT

---

## 1. Project name

```
Kolektif
```

(Name rules: no "Gno" prefix, no implied official affiliation — "Kolektif" is
clean.)

## 2. Tagline (short description, ~120 chars)

```
Rotating savings circles (arisan / ROSCA) that run entirely on gno.land: a realm escrows the pot and renders its own UI.
```

## 3. Description (paste as the long description)

```
Kolektif is a ROSCA — a rotating savings circle, called arisan in Indonesia,
tanda in Latin America, chit fund in India — implemented as a gno.land realm.

A group agrees on a fixed contribution. Everyone pays it every round, and each
round one member takes the whole pot, in a payout order that is fixed at
activation. When the last member has received, the circle closes: collateral
comes back and the penalty fund is shared among the members who never defaulted.

WHY IT IS NOT ANOTHER AMM
Most of the world saves without a bank by rotating a pot between people who
already trust each other. It works, and it fails in exactly two ways: the
treasurer walks off with the pot, or the order is disputed. A ROSCA is the
honest shape of a first on-chain app because it needs no oracle, no liquidation
engine and no counterparty beyond the group — the pot is the group's own money
rotating, so "does this balance?" is a property you can prove.

WHAT THE CHAIN ACTUALLY ENFORCES
1. Exact money in. A payment must carry exactly the collateral or the
   contribution; any other amount reverts the transaction.
2. No overpay, ever. Every payout subtracts from that circle's own pool before
   the send, and the realm panics if a payout would exceed it.
3. No rigged order. The payout order is a Fisher-Yates shuffle over
   sha256(circle id | activation height | sorted member addresses): the creator
   cannot choose who is paid first, and every replay derives the same order.
4. Defaults cost exactly one collateral. After the round deadline, anyone can
   call Advance: non-payers are marked defaulted, their collateral moves to a
   penalty fund, they leave the payout order, and the pot is released from what
   was actually collected. Honest members share the penalty fund at close.

With no defaults a member's net is exactly zero: size contributions out, one
pot of size contributions in, collateral returned. That is asserted end-to-end
in the test suite, including the realm's own balance going to zero at close.

A GENUINE GNO COMPONENT, IN TWO HALVES
- A pure package, rosca, that any realm can import: parameter validation, the
  deterministic schedule, exact splitting of a penalty fund, GNOT formatting,
  ASCII progress bars. It has no state and no realm capability.
- A reference realm that escrows GNOT with chain/banker, runs the state machine,
  emits events, and renders every page as Markdown — no JavaScript, no external
  frontend. The buttons are gnoweb links that prepare the transaction.

INTEGRATION SURFACE
The realm exposes a read-only API (CircleCount, CircleSummary, IsMember,
Standing, GlobalStats) so another realm can gate on membership without touching
Kolektif's state — e.g. a DAO requiring "member in good standing of circle #7"
before an address may vote.

WHAT IS DEPLOYED
- gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif/rosca
- gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif
Both submitted to onyx-1 with gnokey; see DEPLOY.md for tx hashes, the inert
policy on onyx, and the full lifecycle event log.

TESTS
24 tests: schedule determinism and permutation validity, penalty splitting,
formatting, the three-member lifecycle (net zero per member, realm balance empty
at close), default slashing with conservation of value, double-payment guard,
deadline guard, exact-collateral guard, cancellation and refund paths, and a
render smoke test across every page.
```

## 4. Track / category

No required themes. Suggested: **Realm** + **Tool** (the importable package).

## 5. Links

| Field | Value |
|---|---|
| Live deployment | `https://latest.testnets.gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif` |
| Repository | https://github.com/Zerxxz/kolektif |
| Demo video | https://raw.githubusercontent.com/Zerxxz/kolektif/master/demo/demo-kolektif.mp4 — **79s, 1080p, voice-over** (new cut; the source file is also kept as `demo/kolektif-demo-vo.mp4`) |
| Package path | `gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif/rosca` |
| Realm path | `gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif` |
| Deploy tx (rosca) | `5iPsXbOBS/MPhzkXHn3uS1Ul212yeAT8A3hvOkO1he8=` @ height 1,361,013 |
| Deploy tx (realm) | `lsn2zmI0fBFa+hQ1NSbe1CzgOYYNGA0GORcNaWBeDqU=` @ height 1,361,023 |

## 6. Requirements checklist

- [x] Live deployment on the Gno.land **testnet** (onyx-1) — submitted; parked
      by the chain's `inert` policy until an approver enables it (see DEPLOY.md)
- [x] Public code repository — https://github.com/Zerxxz/kolektif
- [x] Genuine Gno component — pure package + realm
- [x] README explaining what it does and how to use it
- [x] Demo video showing it working — `demo/demo-kolektif.mp4` (79s 1080p voice-over; 4 steps: open, join, pay, pot released)
- [x] Short description — section 3 above
- [x] Name does not use a "Gno" prefix

## 7. Discord message (Builder's Room)

Post in the gno.land Discord → `#gnome-tavern-hackathon` (or `#testnets`):

```
Hi all — two packages I submitted to onyx-1 are still parked in
`vm/qinertpaths`:

  gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif/rosca   (h 1,361,013)
  gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif         (h 1,361,023)

I also submitted a one-line control package (…/probe, h 1,360,500) with no
imports at all, and it is parked too — so it looks like gpao is not enabling
submissions on onyx right now, rather than something wrong with my code
(it typechecks and passes `gno test` locally).

Could an approver `MsgEnablePackage` them, or is the oracle being restarted?
Source is in the repo if you want to look before enabling. Thanks!
```

## 8. What to do the moment the packages are enabled

```sh
RPC=https://rpc.onyx.testnets.gno.land:443
ADDR=g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2
KEY=chime

# 1. confirm live
gnokey query vm/qrender -data "gno.land/r/$ADDR/kolektif:" -remote $RPC

# 2. create the demo circle (free, no coins attached)
gnokey maketx call -pkgpath "gno.land/r/$ADDR/kolektif" -func Create \
  -args "Warung Crew" -args 1000000 -args 3 -args 60 \
  -gas-fee 1000000ugnot -gas-wanted 20000000 -chainid onyx-1 -remote $RPC $KEY

# 3. three members join (1 GNOT collateral each) and pay three rounds
#    reuse demo/run_demo.sh verbs with -remote $RPC -chainid onyx-1
```

Then: re-take the 5 screenshots against the testnet URL, re-record or re-link the
video, and replace the "Deployed" table with the onyx tx hashes.

---

## 9. Brand assets

| File | Use |
|---|---|
| `brand/kolektif-logo.png` (1600x512) | listing header / README |
| `brand/kolektif-logo-dark.png` | same lockup on pure black |
| `brand/kolektif-mark.png` (576x576) | square avatar / favicon |
| `brand/kolektif-social-card.png` (1200x630) | DoraHacks thumbnail, posts |

Regenerate with `python3 tools/make_logo.py` (Pillow, no image model): the mark is a stack of
coins inside two rotation arrows — the pot that goes round — drawn at 1x and upscaled with
NEAREST so the pixel grid stays honest. The generator self-tests its glyph table before writing,
so a missing letter fails the build instead of silently clipping a word.

## 10. Spectating and verifying (judge-facing)

Every run has a proof page: `:circle/<id>/party` (linked from the run page's **Proof** section).
It prints, in plain ASCII:

- the payout **order** with seat, player and class per stage;
- the **seed** it was derived from, its **sha256**, and the **activation height**;
- a `VERIFY v1` block (`circle=`, `height=`, `seed=`, `sha256=`, `order=`) made for machines;
- the one command that recomputes it:

```sh
python3 scripts/verify_order.py --rpc https://rpc.onyx.testnets.gno.land:443 --circle 2
```

The script fetches that block over ABCI (no wallet, no SDK), rebuilds the Fisher-Yates order from
the seed with the same `SHA-256(seed:counter)` stream the realm uses, and prints PASS/FAIL. Run
against the local dev chain it prints:

```
sha256     5a11b45a...bdbf  ok
order page 0,1,2
order calc 0,1,2
PASS: the order is exactly what the seed produces
```

That is the difference between "trust our dashboard" and "check our dashboard".

## 11. Accounting invariant (audited 2026-11-26)

The realm keeps a per-circle `Pool` next to the on-chain balance. Every exit path now ends with
`Pool == 0` — including the two that used to strand money:

- **every seat defaulted** → residual returns to the circle's creator (`ResidualReturned`);
- **a round collected money with nobody left to receive it** → the round is refunded to the
  players who paid it (`PotReturned`).

Both are covered by regression tests (`TestAllDefaultStrandsPool`,
`TestPotReturnedWhenNoBeneficiaryLeft`) that fail on the pre-fix code with
`circle pool should be zeroed, got 3000000 ugnot`.

---

## 12. Filed on DoraHacks (2026-11-27 00:00 UTC)

| Field | Value |
|---|---|
| BUIDL | **52072** — https://dorahacks.io/build/52072 |
| Hackathon | Gnome Tavern (id 2470) · track **Default Track** (4783) |
| Submission id | **57867** |
| Status | `0` = DEFAULT — submitted, awaiting organiser confirm (public list shows CONFIRMED only) |
| Logo uploaded | https://cdn.dorahacks.io/static/files/1a21a49a6e66a3576a75a5c4340815e9.png |
| Repo / video | github.com/Zerxxz/kolektif · raw `demo/demo-kolektif.mp4` (79s 1080p voice-over, 23.3 MB) |
| Contacts | discord `axlecrack`, telegram `Nugraha02` |

Form answers: deployment link `https://gno.land/r/<addr>/kolektif`, realm path
`gno.land/r/<addr>/kolektif`, project = new (built 24-27 Nov), country Indonesia, contact as above, KYC = Yes.

**One open gate:** the deployment link only resolves once onyx-1's approval oracle enables the realm. The
url is final and correct; the submission is filed with it. `kolektif-onyx-live-watch` (cron, 10 min) runs the
lifecycle the moment the realm renders, and `gpas.latest.testnets.gno.land/?path=…` is the verdict board to
quote if an organiser asks where the deployment stands.
