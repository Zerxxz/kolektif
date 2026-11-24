# Pesan untuk Discord gno.land — copy-paste

Channel: `#gnome-tavern-hackathon` (atau `#testnets` / `#validators` kalau sepi)

---

```
Hi — onyx-1 package review queue appears stuck, and it's blocking hackathon
submissions.

From https://gpas.latest.testnets.gno.land/ (status board):

  mode: automatic, last pass 2026-11-24T07:11:02Z
  passed: 11 packages
  in review queue: 38 packages

Mine have been "in review queue" all night, across three submissions
(heights quoted from gnokey output):

  gno.land/p/g1udyt8…/kolektif/rosca   h 1,368,314 → 1,370,916 (re-submitted)
  gno.land/r/g1udyt8…/kolektif         h 1,368,317 → 1,370,919 (re-submitted)

Both typecheck and pass `gno test ./...` locally (24 tests), and the realm's
whole import closure is one pure package plus ufmt — no r/sys/users, no gov/dao.
A one-file control package on the same account passed automatically at
2026-11-23T21:05:42Z, so the oracle does reach this account.

Two other observations that suggest it is not just me:
  • 38 packages sit in "in review queue" with only 11 passed in total.
  • Another hackathon entry (…/g1u9frcg…/arisan) is in the same queue.

Could an approver send MsgEnablePackage for the two paths above, or is the
oracle waiting on something specific (a parked import ahead of us)? Happy to
share the repo if you want to read it first:
https://github.com/Zerxxz/kolektif
Thanks!
```

---

Kalau mau lebih pendek, pakai versi ini:

```
onyx-1 review queue looks stuck: gpas board reports 38 packages "in review
queue" vs 11 passed, last pass 07:11Z, and my two (…/kolektif, …/kolektif/rosca,
heights 1,370,916/1,370,919) have been queued all night. They typecheck locally
and a control package on the same account passed at 21:05Z. Can an approver
MsgEnablePackage them, or is the oracle blocked on a parked import ahead?
Repo: https://github.com/Zerxxz/kolektif
```
