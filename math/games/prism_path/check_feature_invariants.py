"""Structural feature-invariant checker over the FULL Prism Path corpus.

Run after EVERY run.py, alongside validate_books.py (which re-scores wins) — this file
guards the FEATURE contract instead. Must print 0 violations before books ship.
    PYTHONPATH=math <venv>/python games/prism_path/check_feature_invariants.py

Replays every book's event stream and asserts the sticky/scatter/beast contract:
  S1  claimed seat persists: every later freegame reveal shows WILD sticky=True at the seat
  S2  claimed seat multiplier never drifts (reveal + prismBeast both match the claim)
  S3  no NON-sticky prismBeast at an already-claimed seat ("normal dragon in a sticky spot")
  S4  no duplicate claims; never more than max_sticky (2) simultaneous claims
  S5  reveal wild set == prismBeast set that spin (no stuck dragons, no phantom beasts)
  S6  prismBeast/prismPath pair 1:1 in order; route[0] = seat; route follows direction to edge
  L1  ARTIFACT INTEGRITY: every published lookUpTable_<mode>_0.csv row's payout column
      matches the same-id book's payoutMultiplier (a stale LUT vs fresh books is torn)
  W1  wincap is TERMINAL: no reveal after it; totals frozen at cap; finalWin == cap
  G1  money grammar: setTotalWin non-decreasing; finalWin == last setTotalWin == payoutMultiplier
  G2  counter grammar: updateFreeSpin totals match trigger+retriggers; amounts increment
  T1  base reveal with >=3 visible scatters => freeSpinTrigger that spin (and converse)
  T2  freegame reveal with >=3 visible scatters => freeSpinRetrigger that spin (and converse)
  T3  trigger/retrigger scatter positions are actual SCAT cells in that reveal
"""
import json
import os
import sys
from collections import Counter

import zstandard

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library", "publish_files")
VIS_ROWS = range(1, 6)  # padded 7-row serialization: visible rows are 1..5

violations = Counter()
examples = {}


def flag(code, book_id, detail):
    violations[code] += 1
    examples.setdefault(code, f"book {book_id}: {detail}")


def dir_route(pos, direction):
    reel, row = pos["reel"], pos["row"]
    out = [(reel, row)]
    if direction == "up":
        out += [(reel, r) for r in range(row - 1, 0, -1)]
    elif direction == "down":
        out += [(reel, r) for r in range(row + 1, 6)]
    elif direction == "left":
        out += [(c, row) for c in range(reel - 1, -1, -1)]
    elif direction == "right":
        out += [(c, row) for c in range(reel + 1, 5)]
    return out


def check_book(book, name):
    bid = f"{name}:{book.get('id')}"
    events = book.get("events", [])
    # split into spins at each reveal
    spins = []
    cur = None
    for ev in events:
        if ev.get("type") == "reveal":
            cur = {"reveal": ev, "events": []}
            spins.append(cur)
        elif cur is not None:
            cur["events"].append(ev)

    claims = {}  # (reel,row) -> {"mult", "spin"}
    for si, spin in enumerate(spins):
        rev = spin["reveal"]
        board = rev["board"]
        gt = rev.get("gameType")
        if gt == "basegame":
            claims = {}  # feature over / not started

        # cell lookup in the padded serialization
        def cell(reel, row):
            return board[reel][row]

        # --- sticky seat persistence (S1, S2) ---
        for (reel, row), c in claims.items():
            if c["spin"] < si:
                s = cell(reel, row)
                if s.get("name") != "WILD" or not s.get("sticky"):
                    flag("S1", bid, f"spin {si}: seat ({reel},{row}) not a sticky WILD in reveal: {s}")
                elif s.get("multiplier") != c["mult"]:
                    flag("S2", bid, f"spin {si}: seat ({reel},{row}) mult {s.get('multiplier')} != claim {c['mult']}")

        # --- beasts this spin ---
        beasts = [e for e in spin["events"] if e.get("type") == "prismBeast"]
        paths = [e for e in spin["events"] if e.get("type") == "prismPath"]
        if len(beasts) != len(paths):
            flag("S6", bid, f"spin {si}: {len(beasts)} beasts vs {len(paths)} paths")
        for b, p in zip(beasts, paths):
            bpos = (b["position"]["reel"], b["position"]["row"])
            ppos = (p["source"]["reel"], p["source"]["row"]) if "source" in p else None
            if ppos != bpos:
                flag("S6", bid, f"spin {si}: beast {bpos} != path source {ppos}")
            route = [(c["position"]["reel"], c["position"]["row"]) for c in p.get("cells", [])]
            expect_full = dir_route(b["position"], b["direction"])
            if route and (route[0] != bpos or route != expect_full[: len(route)]):
                flag("S6", bid, f"spin {si}: route {route} inconsistent with {b['direction']} from {bpos}")

        # S3: non-sticky beast landing on an already-claimed seat
        for b in beasts:
            bpos = (b["position"]["reel"], b["position"]["row"])
            if bpos in claims and claims[bpos]["spin"] < si:
                if not b.get("sticky"):
                    flag("S3", bid, f"spin {si}: NON-sticky beast at claimed seat {bpos}")
                elif b.get("multiplier") != claims[bpos]["mult"]:
                    flag("S2", bid, f"spin {si}: returning beast mult {b.get('multiplier')} != claim")

        # S5: reveal wild set == beast set
        wilds = set()
        for reel in range(5):
            for row in VIS_ROWS:
                if cell(reel, row).get("name") == "WILD":
                    wilds.add((reel, row))
        bset = {(b["position"]["reel"], b["position"]["row"]) for b in beasts}
        if wilds != bset:
            flag("S5", bid, f"spin {si}: reveal wilds {sorted(wilds)} != beasts {sorted(bset)}")

        # register new claims made THIS spin (sticky beast at unclaimed pos)
        for b in beasts:
            bpos = (b["position"]["reel"], b["position"]["row"])
            if b.get("sticky") and bpos not in claims:
                claims[bpos] = {"mult": b.get("multiplier"), "spin": si}
        if len(claims) > 2:
            flag("S4", bid, f"spin {si}: {len(claims)} simultaneous claims")

        # --- scatter/trigger integrity (T1..T3) ---
        scats = [(reel, row) for reel in range(5) for row in VIS_ROWS if cell(reel, row).get("name") == "SCAT"]
        trig = next((e for e in spin["events"] if e.get("type") == "freeSpinTrigger"), None)
        retrig = next((e for e in spin["events"] if e.get("type") == "freeSpinRetrigger"), None)
        if gt == "basegame":
            if len(scats) >= 3 and not trig:
                flag("T1", bid, f"spin {si}: {len(scats)} scatters visible but NO freeSpinTrigger")
            if trig and len(scats) < 3:
                flag("T1", bid, f"spin {si}: trigger with only {len(scats)} scatters visible")
        else:
            if len(scats) >= 3 and not retrig:
                flag("T2", bid, f"spin {si}: {len(scats)} scatters visible in freegame but NO retrigger")
            if retrig and len(scats) < 3:
                flag("T2", bid, f"spin {si}: retrigger with only {len(scats)} scatters visible")
        for e in (trig, retrig):
            if e:
                for p in e.get("positions", []):
                    if (p["reel"], p["row"]) not in scats:
                        flag("T3", bid, f"spin {si}: trigger position {p} is not a SCAT cell")


CAP = 500000  # 5000x in x100 book units


def check_grammar(book, bid):
    events = book.get("events", [])
    # W1: the cap terminates the round
    cap_idx = next((i for i, e in enumerate(events) if e.get("type") == "wincap"), None)
    if cap_idx is not None:
        for e in events[cap_idx + 1 :]:
            if e.get("type") == "reveal":
                flag("W1", bid, "reveal AFTER wincap — cap must terminate the round")
                break
        for e in events[cap_idx + 1 :]:
            if e.get("type") in ("setTotalWin", "finalWin") and e.get("amount") != CAP:
                flag("W1", bid, f"post-cap {e['type']} {e.get('amount')} != cap")
        if book.get("payoutMultiplier") != CAP:
            flag("W1", bid, f"capped book payoutMultiplier {book.get('payoutMultiplier')} != cap")

    # G1: money never decreases; the book closes consistently
    totals = [e.get("amount") for e in events if e.get("type") == "setTotalWin"]
    for a, b in zip(totals, totals[1:]):
        if b < a:
            flag("G1", bid, f"setTotalWin decreased {a} -> {b}")
            break
    finals = [e.get("amount") for e in events if e.get("type") == "finalWin"]
    if len(finals) != 1:
        flag("G1", bid, f"{len(finals)} finalWin events (must be exactly 1)")
    elif totals and finals[0] != totals[-1]:
        flag("G1", bid, f"finalWin {finals[0]} != last setTotalWin {totals[-1]}")
    elif finals and finals[0] != book.get("payoutMultiplier"):
        flag("G1", bid, f"finalWin {finals[0]} != payoutMultiplier {book.get('payoutMultiplier')}")

    # G2: free-spin counter arithmetic
    trig = next((e for e in events if e.get("type") == "freeSpinTrigger"), None)
    if trig is not None:
        updates = [e for e in events if e.get("type") == "updateFreeSpin"]
        retrigs = [e for e in events if e.get("type") == "freeSpinRetrigger"]
        expected_total = trig.get("totalFs", 0)
        for e in events:
            if e.get("type") == "updateFreeSpin":
                if e.get("total") != expected_total:
                    flag("G2", bid, f"updateFreeSpin total {e.get('total')} != expected {expected_total}")
                    break
            elif e.get("type") == "freeSpinRetrigger":
                expected_total = e.get("totalFs", expected_total)
        amounts = [e.get("amount") for e in updates]
        if amounts != list(range(len(amounts))):
            flag("G2", bid, f"updateFreeSpin amounts not 0..n-1: {amounts[:8]}...")
        final_total = expected_total
        # a capped feature legitimately stops early; otherwise all awarded spins play
        if cap_idx is None and len(updates) != final_total:
            flag("G2", bid, f"{len(updates)} free spins played, {final_total} awarded (no cap)")


# dragon feature spins guarantee N dragons on the FIRST reveal (D1)
GUARANTEE = {"books_dragon3": 3, "books_dragon5": 5}


def check_guarantee(book, name):
    key = name.split(".")[0]
    need = GUARANTEE.get(key)
    if not need:
        return
    rev = next((e for e in book.get("events", []) if e.get("type") == "reveal"), None)
    if rev is None:
        return
    wilds = sum(
        1 for reel in rev["board"] for r in VIS_ROWS if reel[r].get("name") == "WILD"
    )
    if wilds < need:
        flag("D1", f"{key}:{book.get('id')}", f"first reveal has {wilds} dragons, guarantee is {need}")


import csv as _csv
import glob as _glob


def check_lookup_tables():
    """L1: published LUT payout column must equal the book payoutMultiplier for every id."""
    for lut_path in sorted(_glob.glob(os.path.join(LIB, "lookUpTable_*_0.csv"))):
        mode = os.path.basename(lut_path)[len("lookUpTable_") : -len("_0.csv")]
        books_path = os.path.join(LIB, f"books_{mode}.jsonl.zst")
        if not os.path.exists(books_path):
            flag("L1", f"lut:{mode}", "published LUT has no matching books file")
            continue
        raw = zstandard.ZstdDecompressor().stream_reader(open(books_path, "rb")).read()
        pay_by_id = {}
        for line in raw.split(b"\n"):
            if line.strip():
                b = json.loads(line)
                pay_by_id[b.get("id")] = b.get("payoutMultiplier")
        n_bad = 0
        for row in _csv.reader(open(lut_path)):
            if len(row) < 3:
                continue
            try:
                bid, pay = int(row[0]), float(row[2])
            except ValueError:
                continue
            if bid in pay_by_id and abs(pay_by_id[bid] - pay) > 0.5:
                if n_bad == 0:
                    flag("L1", f"lut:{mode}", f"id {bid}: LUT {pay} != book {pay_by_id[bid]}")
                n_bad += 1
        if n_bad > 1:
            violations["L1"] += n_bad - 1


total = 0
for fname in sorted(os.path.basename(p) for p in _glob.glob(os.path.join(LIB, "books_*.jsonl.zst"))):
    raw = zstandard.ZstdDecompressor().stream_reader(open(os.path.join(LIB, fname), "rb")).read()
    for line in raw.split(b"\n"):
        if not line.strip():
            continue
        book = json.loads(line)
        check_book(book, fname.split(".")[0])
        check_guarantee(book, fname)
        check_grammar(book, f"{fname.split('.')[0]}:{book.get('id')}")
        total += 1

check_lookup_tables()
print(f"checked {total} books")
if not violations:
    print("ALL FEATURE INVARIANTS HOLD (S1-S6, T1-T3, D1, W1, G1-G2, L1): 0 violations")
    sys.exit(0)
for code, n in sorted(violations.items()):
    print(f"{code}: {n} violations — first: {examples[code]}")
sys.exit(1)
