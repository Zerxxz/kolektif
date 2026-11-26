package kolektif

import (
	"strings"
	"testing"

	"gno.land/p/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/roscasched"
	"gno.land/p/nt/testutils/v0"
)

// TestPartyPageCarriesVerifiableProof covers the spectate page: it must render
// without a wallet, expose the machine-readable block, and print the order the
// seed actually produces (so the page can be checked, not trusted).
func TestPartyPageCarriesVerifiableProof(cur realm, t *testing.T) {
	reset()
	for _, name := range []string{"alice", "bob", "carol"} {
		fund(testutils.TestAddress(name), 10*gnot)
	}
	id := newFilledCircle(cross(cur), t, 1*gnot, 60)
	c := mustCircle(id)

	page := Render("circle/1/party")
	for _, want := range []string{"VERIFY v1", "seed=1|", "sha256=", "order=", "Payout order"} {
		if !strings.Contains(page, want) {
			t.Fatalf("party page should contain %q", want)
		}
	}

	// The order printed must equal the order recomputed from the same seed.
	want := ""
	for i, idx := range roscasched.Order(len(c.Members), c.Seed) {
		if i > 0 {
			want += ","
		}
		want += itoa(idx)
	}
	if !strings.Contains(page, "order="+want) {
		t.Fatalf("party page order does not match the seed: want order=%s", want)
	}

	// Same seed, same order, twice: determinism is the whole claim.
	a := roscasched.Order(len(c.Members), c.Seed)
	b := roscasched.Order(len(c.Members), c.Seed)
	for i := range a {
		if a[i] != b[i] {
			t.Fatalf("order is not deterministic at %d: %d vs %d", i, a[i], b[i])
		}
	}

	// And the run page links to it.
	if !strings.Contains(Render("circle/1"), ":circle/1/party") {
		t.Fatalf("run page should link to the party page")
	}
}

func itoa(v int) string {
	if v == 0 {
		return "0"
	}
	out := ""
	for v > 0 {
		out = string(rune('0'+v%10)) + out
		v /= 10
	}
	return out
}
