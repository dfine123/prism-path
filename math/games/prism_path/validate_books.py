"""Prism Path — book invariant validator + INDEPENDENT WIN RE-EVALUATION (the audit gate).

Walks EVERY generated book and:
  A) asserts the frontend-rendering invariants (un-resolved wilds, beast/path parity,
     payout sanity), and
  B) RE-COMPUTES every spin's line wins from scratch — from the reveal board + prismPath
     events, using the configured paylines/paytable/wild rules — and FAILS on any mismatch
     with the book's recorded winInfo. This catches payline-set drift, paytable drift,
     evaluator bugs and multiplier errors before anything ships.

Run after run.py, from the math/ root:
    env/Scripts/python.exe games/prism_path/validate_books.py
Exits non-zero with offending books listed on any violation.
"""
import glob
import json
import os
import sys
from collections import defaultdict

import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # game_config (src.* resolves from the math/ root cwd)

from game_config import GameConfig  # noqa: E402

LIB = os.path.join(HERE, "library", "publish_files")
WIN_CAP_X = 5000  # payoutMultiplier is x100 -> cap*100
CFG = GameConfig()


def read_books(name):
    path = os.path.join(LIB, name)
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        data = zstandard.ZstdDecompressor().stream_reader(f).read()
    return [json.loads(line) for line in data.split(b"\n") if line.strip()]


# ---------- A) rendering invariants ----------

def validate_rendering(bk):
    out = []
    events = bk.get("events", [])
    bid = bk.get("id")

    pm = bk.get("payoutMultiplier")
    if pm is None or pm < 0:
        out.append(f"book {bid}: bad payoutMultiplier={pm}")
    elif pm > WIN_CAP_X * 100:
        out.append(f"book {bid}: payoutMultiplier {pm} exceeds cap {WIN_CAP_X*100}")

    n_beast = sum(1 for e in events if e["type"] == "prismBeast")
    n_path = sum(1 for e in events if e["type"] == "prismPath")
    if n_beast != n_path:
        out.append(f"book {bid}: prismBeast({n_beast}) != prismPath({n_path}) parity")

    reveal_no = 0
    for i, e in enumerate(events):
        if e["type"] != "reveal":
            continue
        reveal_no += 1
        wilds = {}
        for reel, col in enumerate(e["board"]):
            for row, cell in enumerate(col):
                if row == 0 or row == len(col) - 1:
                    continue  # padding rows are off-screen
                if cell.get("name") == "WILD":
                    m = cell.get("multiplier")
                    wilds[(reel, row)] = m if isinstance(m, (int, float)) else 0
        covered = set()
        for f in events[i + 1:]:
            if f["type"] == "reveal":
                break
            if f["type"] == "prismPath":
                for c in f.get("cells", []):
                    pos = c["position"]
                    covered.add((pos["reel"], pos["row"]))
            if f["type"] == "prismBeast":
                pos = f["position"]
                covered.add((pos["reel"], pos["row"]))
        for (reel, row), m in wilds.items():
            if m <= 1 and (reel, row) not in covered:
                out.append(
                    f"book {bid} reveal#{reveal_no} cell ({reel},{row}): WILD un-resolved -> stuck beast"
                )
    return out


# ---------- B) independent win re-evaluation ----------

def split_spins(events):
    """Each reveal starts a spin; attach its prismPath + winInfo events."""
    spins = []
    cur = None
    for e in events:
        if e["type"] == "reveal":
            cur = {"reveal": e, "paths": [], "win_info": None}
            spins.append(cur)
        elif cur is not None:
            if e["type"] == "prismPath":
                cur["paths"].append(e)
            elif e["type"] == "winInfo":
                cur["win_info"] = e
    return spins


def reevaluate_spin(spin):
    """Recompute this spin's line wins from the reveal + paths. Returns (total_x, wins_list)."""
    board = spin["reveal"]["board"]
    width = len(board)
    height = len(board[0]) - 2  # strip padding rows

    names = [[board[r][row + 1].get("name") for row in range(height)] for r in range(width)]

    # each prismPath event = one distinct beast: its multiplier over its covered cells
    beast_sets = defaultdict(dict)  # (reel,row) -> {beast_index: mult}
    for bi, pe in enumerate(spin["paths"]):
        mult = pe.get("multiplier") or (pe["cells"][0]["multiplier"] if pe.get("cells") else 1)
        for c in pe.get("cells", []):
            rr = (c["position"]["reel"], c["position"]["row"] - 1)
            beast_sets[rr][bi] = int(mult)

    def is_wild(r, row):
        return names[r][row] == "WILD" or (r, row) in beast_sets

    total = 0.0
    wins = []
    for line_index, line in CFG.paylines.items():
        first_wild = is_wild(0, line[0])
        first_non_wild = None if first_wild else names[0][line[0]]
        wild_matches = 1 if first_wild else 0
        matches = 0 if first_wild else 1
        for reel in range(1, width):
            row = line[reel]
            if first_non_wild is not None:
                if names[reel][row] == first_non_wild or is_wild(reel, row):
                    matches += 1
                else:
                    break
            else:
                if is_wild(reel, row):
                    wild_matches += 1
                elif names[reel][row] in ("SCAT",):
                    break
                else:
                    first_non_wild = names[reel][row]
                    matches += 1

        wild_win = CFG.paytable.get((wild_matches, "WILD"), 0.0)
        base_win = 0.0
        if first_non_wild is not None:
            base_win = CFG.paytable.get((wild_matches + matches, first_non_wild), 0.0)

        if base_win <= 0 and wild_win <= 0:
            continue
        # rule: a completing symbol always registers the FULL line; pure wild-run otherwise
        if wild_win > 0 and base_win <= 0:
            kind = wild_matches
            pay = wild_win
        else:
            kind = wild_matches + matches
            pay = base_win

        # line multiplier: product of DISTINCT beasts intersecting the winning positions
        seen = {}
        for reel in range(kind):
            seen.update(beast_sets.get((reel, line[reel]), {}))
        mult = 1
        for m in seen.values():
            mult *= m
        mult = min(max(mult, 1), 100_000)  # mirror the strategy clamp

        total += round(pay * mult, 2)
        wins.append({"lineIndex": line_index, "kind": kind, "win": round(pay * mult, 2)})

    return round(total, 2), wins


def validate_wins(bk):
    out = []
    bid = bk.get("id")
    cap_x100 = WIN_CAP_X * 100
    cum = 0  # recomputed cumulative for the ROUND (x100, uncapped)
    for si, spin in enumerate(split_spins(bk.get("events", []))):
        exp_total, exp_wins = reevaluate_spin(spin)
        exp_x100 = round(exp_total * 100)
        wi = spin["win_info"]
        rec_total_x100 = wi.get("totalWin", 0) if wi else 0

        if cum + exp_x100 >= cap_x100:
            # WIN-CAP zone: the engine truncates the ROUND at 5000x. The recorded spin total
            # may be clamped; it must never EXCEED the raw recomputed value, and a round that
            # crosses the cap must pay out exactly the cap.
            if rec_total_x100 > exp_x100 + 1:
                out.append(
                    f"book {bid} spin#{si}: capped spin recorded {rec_total_x100} > recomputed {exp_x100}"
                )
            if bk.get("payoutMultiplier") != cap_x100:
                out.append(
                    f"book {bid} spin#{si}: crosses the cap but book payout {bk.get('payoutMultiplier')} != {cap_x100}"
                )
            cum += exp_x100
            continue
        cum += exp_x100

        if abs(exp_x100 - rec_total_x100) > 1:  # 1 = rounding tolerance
            out.append(
                f"book {bid} spin#{si}: recomputed {exp_x100} != recorded {rec_total_x100}"
            )
            continue
        rec_wins = wi.get("wins", []) if wi else []
        if len(exp_wins) != len(rec_wins):
            out.append(
                f"book {bid} spin#{si}: recomputed {len(exp_wins)} wins != recorded {len(rec_wins)}"
            )
            continue
        rec_keys = sorted((w["meta"]["lineIndex"], w["kind"]) for w in rec_wins)
        exp_keys = sorted((w["lineIndex"], w["kind"]) for w in exp_wins)
        if rec_keys != exp_keys:
            out.append(f"book {bid} spin#{si}: line/kind mismatch {exp_keys} != {rec_keys}")
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
            v = validate_rendering(bk) + validate_wins(bk)
            if v:
                bad_books += 1
                mode_bad += 1
                if len(samples) < 20:
                    samples.extend(v[:2])
        print(f"  {name}: {len(books)} books, {mode_bad} with violations")

    print(f"\nvalidated {total} books total (rendering + independent win re-evaluation); {bad_books} with violations")
    for s in samples:
        print("   -", s)
    if bad_books:
        print("\nFAIL: book invariants violated.")
        sys.exit(1)
    print("\nPASS: all books satisfy rendering invariants AND independent win re-evaluation.")
    sys.exit(0)


if __name__ == "__main__":
    main()
