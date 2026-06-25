"""Generate flat/placeholder Phase-1 reelstrips for Prism Path (reproducible).

Each reel column is 50 symbols with a fixed composition, shuffled deterministically.
Beasts (WILD) appear ~6% (base) / ~10% (free) per cell so the feature shows up during
random play. Phase 2 replaces these with weighted strips tuned for true rarity + RTP.
Run:  python games/prism_path/reels/_gen_reels.py
"""

import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))


def make_column(counts: dict, seed: int) -> list:
    rng = random.Random(seed)
    items = []
    for sym, n in counts.items():
        items += [sym] * n
    rng.shuffle(items)
    return items


def write_reel(filename: str, counts: dict, base_seed: int) -> None:
    cols = [make_column(counts, base_seed + i) for i in range(5)]
    length = len(cols[0])
    rows = [[cols[c][r] for c in range(5)] for r in range(length)]
    with open(os.path.join(HERE, filename), "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"wrote {filename}: {length} rows x 5 reels")


# Rarer beasts/scatters: base beast is RARE (~4%); free a bit denser but not saturating; scatters
# sparse so free-spin triggers + retriggers stay rare (sticky feature escalates without always capping).
BR0 = {"L1": 6, "L2": 6, "L3": 7, "L4": 7, "L5": 8, "H1": 4, "H2": 4, "H3": 3, "H4": 2, "WILD": 2, "SCAT": 1}
FR0 = {"L1": 6, "L2": 7, "L3": 7, "L4": 7, "L5": 8, "H1": 4, "H2": 4, "H3": 3, "H4": 1, "WILD": 2, "SCAT": 1}

if __name__ == "__main__":
    assert sum(BR0.values()) == 50 and sum(FR0.values()) == 50
    write_reel("BR0.csv", BR0, 100)
    write_reel("FR0.csv", FR0, 200)
    print("reels written")
