package kolektif

import (
	"testing"

	"gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/rosca"
	"gno.land/p/nt/testutils/v0"
)

// TestAllDefaultStrandsPool is the audit regression: if every seat misses the
// round, every collateral is slashed into the penalty fund, nobody is honest,
// and the circle closes. Either the pool must leave the realm or the realm is
// permanently holding money nobody can claim.
func TestAllDefaultStrandsPool(cur realm, t *testing.T) {
	reset()
	alice := testutils.TestAddress("alice")
	bob := testutils.TestAddress("bob")
	carol := testutils.TestAddress("carol")
	start := int64(10) * gnot
	fund(alice, start)
	fund(bob, start)
	fund(carol, start)

	id := newFilledCircle(cross(cur), t, 1*gnot, 60)
	before := balanceOf(realmAddr)
	if before != 3*gnot {
		t.Fatalf("realm should hold the three collaterals, holds %d", before)
	}

	// Nobody pays round 0; the deadline passes and anyone settles it.
	testing.SkipHeights(30)
	testing.SetRealm(testing.NewUserRealm(alice))
	Advance(cross(cur), id)

	c := mustCircle(id)
	if c.Status != rosca.StatusComplete {
		t.Fatalf("every seat defaulted, circle should be complete, got %s", c.Status.String())
	}
	if c.Pool != 0 {
		t.Fatalf("circle pool should be zeroed, got %d ugnot", c.Pool)
	}
	if got := balanceOf(realmAddr); got != 0 {
		t.Fatalf("realm must hold nothing after total default, holds %d ugnot", got)
	}
}

// TestPotReturnedWhenNoBeneficiaryLeft covers the narrower leak: a round
// collects money but every remaining seat has either received or defaulted, so
// there is nobody to pay. The payers must get their money back, not the realm.
func TestPotReturnedWhenNoBeneficiaryLeft(cur realm, t *testing.T) {
	reset()
	alice := testutils.TestAddress("alice")
	bob := testutils.TestAddress("bob")
	carol := testutils.TestAddress("carol")
	start := int64(10) * gnot
	fund(alice, start)
	fund(bob, start)
	fund(carol, start)

	id := newFilledCircle(cross(cur), t, 1*gnot, 60)

	// Round 0: everyone pays, so the first beneficiary receives the pot.
	for _, m := range []address{alice, bob, carol} {
		testing.SetRealm(testing.NewUserRealm(m))
		payFrom(1 * gnot)
		Contribute(cross(cur), id)
	}
	c := mustCircle(id)
	first := c.Members[c.Order[0]].Addr

	// Round 1: only alice pays, then the deadline passes and everyone else
	// (including the round-0 winner) is settled as a default.
	testing.SetRealm(testing.NewUserRealm(alice))
	payFrom(1 * gnot)
	Contribute(cross(cur), id)
	testing.SkipHeights(30)
	testing.SetRealm(testing.NewUserRealm(bob))
	Advance(cross(cur), id)

	c = mustCircle(id)
	if c.Status != rosca.StatusComplete {
		t.Fatalf("circle should be complete, got %s", c.Status.String())
	}
	if c.Pool != 0 {
		t.Fatalf("pool should be empty, got %d", c.Pool)
	}
	if got := balanceOf(realmAddr); got != 0 {
		t.Fatalf("realm must hold nothing, holds %d", got)
	}
	// The round-1 contribution alice paid must have come back to her, either as
	// a "return" payout or inside the close-out refund.
	returned := false
	for _, p := range c.Payouts {
		if p.To == alice && (p.Kind == "return" || p.Kind == "refund") {
			returned = true
		}
	}
	if !returned {
		t.Fatalf("alice paid round 1 but got no payout back; payouts: %v", c.Payouts)
	}
	_ = first
}
