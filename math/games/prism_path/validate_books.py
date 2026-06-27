"""Prism Path — book invariant validator (frontend-rendering safety gate).

Walks EVERY generated book and asserts the invariants the front end relies on, so a book that
would render incorrectly can never ship. Run after run.py, from the math/ root:

    env/Scripts/python.exe games/prism_path/validate_books.py

Exits non-zero (and prints offending books) if any invariant fails — wire it into the build so a
regression like "a beast landed but never activated" is caught automatically, not by eyeballing.

Invariants checked per book:
  1. NO UN-RESOLVED WILD: every WILD cell in a reveal either carries multiplier>1 (a sticky wild that
     renders from the reveal) OR is covered by a prismPath event before the next reveal (a new beast
     that animates into a multiplier wild). A WILD with no multiplier and no path = the "stuck beast"
     bug — the whole reason this file exists.
  2. BEAST/PATH PARITY: every prismBeast has a matching prismPath (a beast that drops must travel).
  3. PAYOUT SANITY: payoutMultiplier is present, non-negative, and within the win cap.
"""
import glob
import json
import os
import sys

import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "library", "publish_files")
WIN_CAP_X = 5000  # payoutMultiplier is x100 -> cap*100


def read_books(name):
    path = os.path.join(LIB, name)
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        data = zstandard.ZstdDecompressor().stream_reader(f).read()
    return [json.loads(line) for line in data.split(b"\n") if line.strip()]


def validate_book(bk):
    out = []
    events = bk.get("events", [])
    bid = bk.get("id")

    # payout sanity
    pm = bk.get("payoutMultiplier")
    if pm is None or pm < 0:
        out.append(f"book {bid}: bad payoutMultiplier={pm}")
    elif pm > WIN_CAP_X * 100:
        out.append(f"book {bid}: payoutMultiplier {pm} exceeds cap {WIN_CAP_X*100}")

    n_beast = sum(1 for e in events if e["type"] == "prismBeast")
    n_path = sum(1 for e in events if e["type"] == "prismPath")
    if n_beast != n_path:
        out.append(f"book {bid}: prismBeast({n_beast}) != prismPath({n_path}) parity")

    # per-reveal un-resolved-wild check
    reveal_no = 0
    for i, e in enumerate(events):
        if e["type"] != "reveal":
            continue
        reveal_no += 1
        wilds = {}
        for reel, col in enumerate(e["board"]):
            for row, cell in enumerate(col):
                if row == 0 or row == len(col) - 1:
                    continue  # padding rows are off-screen (spin scroll) — not player-visible
                if cell.get("name") == "WILD":
                    m = cell.get("multiplier")
                    wilds[(reel, row)] = m if isinstance(m, (int, float)) else 0
        # prismPath coverage until the next reveal
        covered = set()
        for f in events[i + 1:]:
            if f["type"] == "reveal":
                break
            if f["type"] == "prismPath":
                for c in f.get("cells", []):
                    pos = c["position"]
                    covered.add((pos["reel"], pos["row"]))
        for (reel, row), m in wilds.items():
            if m <= 1 and (reel, row) not in covered:
                out.append(
                    f"book {bid} reveal#{reveal_no} cell ({reel},{row}): WILD mult={m} un-resolved "
                    f"(no multiplier and no prismPath) -> would render as a stuck beast"
                )
    return out


def main():
    total = 0
    bad_books = 0
    samples = []
    for name in ("books_base.jsonl.zst", "books_bonus.jsonl.zst", "books_super.jsonl.zst"):
        books = read_books(name)
        if not books:
            print(f"  (skip {name}: not found)")
            continue
        mode_bad = 0
        for bk in books:
            total += 1
            v = validate_book(bk)
            if v:
                bad_books += 1
                mode_bad += 1
                if len(samples) < 25:
                    samples.extend(v[:2])
        print(f"  {name}: {len(books)} books, {mode_bad} with violations")

    print(f"\nvalidated {total} books total; {bad_books} with violations")
    for s in samples:
        print("   -", s)
    if bad_books:
        print("\nFAIL: book invariants violated.")
        sys.exit(1)
    print("\nPASS: all books satisfy frontend-rendering invariants.")
    sys.exit(0)


if __name__ == "__main__":
    main()
