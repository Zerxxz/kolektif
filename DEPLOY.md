# Deploy log — onyx-1

Everything below is copied from real `gnokey` output, not transcribed by hand.

## Network

| | |
|---|---|
| Chain id | `onyx-1` (current gno.land testnet, "Test17") |
| RPC | `https://rpc.onyx.testnets.gno.land:443` |
| Deployer key | `g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2` |
| Toolchain | `gno v1.8.0` release binaries |

## Transactions

**1. Pure package — `rosca`**

```
$ gnokey maketx addpkg -pkgpath gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif/rosca \
    -pkgdir gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif/rosca \
    -gas-fee 1000000ugnot -gas-wanted 20000000 -chainid onyx-1 chime
OK!
GAS USED:   18266868
HEIGHT:     1360357
TX HASH:    rS5UBdp2TViOjpLUFkS0CjepDXP3aHh82i0alGl0JLE=
```

**2. Realm — `kolektif`**

```
$ gnokey maketx addpkg -pkgpath gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif \
    -pkgdir gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif \
    -gas-fee 2000000ugnot -gas-wanted 60000000 -chainid onyx-1 chime
OK!
GAS USED:   59121207
HEIGHT:     1360362
TX HASH:    NTZXlBtXAN72lJ/QslJ5cgKA45N3YBEQD4/mVphWPVY=
```

## The `inert` gate on onyx-1

onyx-1 (like mainnet) runs with:

```
vm:p:code_submission_policy = "inert"
vm:p:pkg_approvers         = [g1yaee4f…, g1m0rgan…, g1manfred…, g1ecsuj…, g19p3yz…, g1xnv89…, g1lnkyt…]
```

Under `inert`, `MsgAddPackage` stores the package but does not run it: the code is
not typechecked, not executed and not importable until an address in
`pkg_approvers` sends `MsgEnablePackage`. The chain's approval oracle (`gpao`)
does that automatically for packages it can verify inside its time budget.

Confirmed parked with `vm/qinertpaths`:

```
$ gnokey query vm/qinertpaths -remote https://rpc.onyx.testnets.gno.land:443
gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif/rosca
gno.land/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif
```

A control experiment shows this is not specific to this code: a minimal package
containing one `func Ping() string { return "pong" }` and importing nothing
(`gno.land/p/<addr>/probe`, height 1360500) stays parked for the same period, so
the oracle is not currently enabling submissions on onyx at all.

While parked the realm still resolves from any node that has the source, so the
full lifecycle below runs unchanged on a local `gnodev` chain — and will run on
onyx unchanged once the packages are enabled.

## Full lifecycle, executed on a chain (dev chain, `gnodev`)

`demo/run_demo.sh` drives three premined members (`alice`, `bob`, `carol`) through
a 3-seat circle at 1 GNOT per round. Events emitted, as returned by `gnokey`:

```
CircleCreated     id=1 contribution=1000000 size=3
MemberJoined      id=1 seats=1
MemberJoined      id=1 seats=2
MemberJoined      id=1 seats=3
CircleActivated   id=1 height=9 seed=1|9|g1duh0u…,g1g6rha…,g1vkc6d…
PotPaid           round=0 to=g1duh0u…  amount=3000000
PotPaid           round=1 to=g1vkc6d…  amount=3000000
PotPaid           round=2 to=g1g6rha…  amount=3000000
CircleClosed      id=1 paidOut=12000000
```

Post-conditions checked on chain:

- every member received the pot exactly once (`pot received: yes`),
- collateral was returned to all three (`collateral: returned`),
- the realm address balance is **empty** after close,
- `Paid in 9 GNOT · paid out 12 GNOT · residual in realm 0 GNOT` (the extra 3
  GNOT is the returned collateral, not a payout to a member).

## Deploy script (re-run on any network)

```sh
RPC=https://rpc.onyx.testnets.gno.land:443
ADDR=g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2
KEY=chime

gnokey maketx addpkg \
  -pkgpath "gno.land/p/$ADDR/kolektif/rosca" \
  -pkgdir "gno.land/p/$ADDR/kolektif/rosca" \
  -gas-fee 1000000ugnot -gas-wanted 20000000 \
  -chainid onyx-1 -remote $RPC $KEY

gnokey maketx addpkg \
  -pkgpath "gno.land/r/$ADDR/kolektif" \
  -pkgdir "gno.land/r/$ADDR/kolektif" \
  -gas-fee 2000000ugnot -gas-wanted 60000000 \
  -chainid onyx-1 -remote $RPC $KEY
```

Order matters: the realm imports the package, so the package must be submitted
first.
