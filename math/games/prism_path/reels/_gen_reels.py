"""Generate Prism Path reelstrips — Phase 2: per-reel weighted 100-row strips.

Shaping goals (operator direction, 2026-08-04):
  * ROYALS low-but-fair and COMMON — they carry board texture, not value.
  * GEM LADDER by value: purple H4 (entry, most common) -> green H3 -> blue H2 ->
    red H1 (premium, rarest, thinner on reels 1-2 so 5-kind starts are earned).
  * DRAGON (WILD) actually rare: E[dragons/board] ~= 0.40 base (P>=1 ~ 1 in 3 spins)
    instead of the old 1.0/board (2 of 3 spins) — path lines must feel like an event.
  * SCATTER thinned on reels 4-5: natural trigger ~= 1/220 base (the pricing anchor
    is 1/200; the old uniform strips hit ~1/116).
  * FREE strips: more dragons (E ~= 0.65), scatters sparse (retrigger stays rare).

Each reel is an independent 100-symbol column, deterministically shuffled.
Run:  python games/prism_path/reels/_gen_reels.py
"""

import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
STRIP_LEN = 100
ROYALS = ("L2", "L3", "L4", "L5")
# royal mix within the filler share (A slightly scarcer than J — it pays a touch more)
ROYAL_MIX = {"L2": 0.21, "L3": 0.24, "L4": 0.27, "L5": 0.28}


def build_column(specials: dict, seed: int) -> list:
    """specials: symbol -> count for non-royals; royals auto-fill the remainder."""
    used = sum(specials.values())
    fill = STRIP_LEN - used
    counts = dict(specials)
    acc = 0
    for i, sym in enumerate(ROYALS):
        n = round(fill * ROYAL_MIX[sym]) if i < len(ROYALS) - 1 else fill - acc
        counts[sym] = n
        acc += n
    assert sum(counts.values()) == STRIP_LEN, counts
    rng = random.Random(seed)
    items = []
    for sym, n in counts.items():
        items += [sym] * n
    rng.shuffle(items)
    return items


def write_reel(filename: str, per_reel: list, base_seed: int) -> None:
    cols = [build_column(per_reel[i], base_seed + i) for i in range(5)]
    rows = [[cols[c][r] for c in range(5)] for r in range(STRIP_LEN)]
    with open(os.path.join(HERE, filename), "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"wrote {filename}: {STRIP_LEN} rows x 5 reels")


# ---- BASE strips: per-reel non-royal counts (royals fill to 100) ----
BR0_REELS = [
    {"WILD": 2, "SCAT": 2, "H1": 3, "H2": 5, "H3": 6, "H4": 8},  # reel 1
    {"WILD": 2, "SCAT": 2, "H1": 3, "H2": 5, "H3": 6, "H4": 8},  # reel 2
    {"WILD": 1, "SCAT": 2, "H1": 4, "H2": 5, "H3": 6, "H4": 8},  # reel 3
    {"WILD": 2, "SCAT": 1, "H1": 4, "H2": 5, "H3": 6, "H4": 8},  # reel 4
    {"WILD": 1, "SCAT": 1, "H1": 4, "H2": 5, "H3": 6, "H4": 8},  # reel 5
]

# ---- FREE strips: denser dragons, same gem ladder, scatters sparse ----
FR0_REELS = [
    {"WILD": 3, "SCAT": 1, "H1": 3, "H2": 5, "H3": 6, "H4": 8},
    {"WILD": 3, "SCAT": 1, "H1": 3, "H2": 5, "H3": 6, "H4": 8},
    {"WILD": 2, "SCAT": 1, "H1": 4, "H2": 5, "H3": 6, "H4": 8},
    {"WILD": 3, "SCAT": 1, "H1": 4, "H2": 5, "H3": 6, "H4": 8},
    {"WILD": 2, "SCAT": 1, "H1": 4, "H2": 5, "H3": 6, "H4": 8},
]

if __name__ == "__main__":
    write_reel("BR0.csv", BR0_REELS, 100)
    write_reel("FR0.csv", FR0_REELS, 200)
    # sanity: expected dragons per 5x5 board window (5 visible cells per reel)
    for name, spec in (("BR0", BR0_REELS), ("FR0", FR0_REELS)):
        e = sum(5 * r["WILD"] / STRIP_LEN for r in spec)
        print(f"{name}: E[dragons/board] = {e:.2f}")
    print("reels written")
