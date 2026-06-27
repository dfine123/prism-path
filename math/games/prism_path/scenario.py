"""Prism Path — scenario controller (Phase-1 forced-outcome tool).

Force any Prism Beast outcome and emit a playable one-entry book (matching the real math
output format) that the frontend can play directly. This is the primary feel-test tool.

Examples (run from the math/ root):
    python games/prism_path/scenario.py --preset overlap
    python games/prism_path/scenario.py --preset whiff
    python games/prism_path/scenario.py --beast 2,2 right 3 --beast 0,0 down 5 --name custom
    python games/prism_path/scenario.py --all            # write every preset to scenario_books.json

--beast takes:  reel,row  direction(up|down|left|right)  multiplier
Output is written to games/prism_path/library/scenarios/ (single book per preset, plus a
combined scenario_books.json keyed by name for the frontend stories).
"""

import argparse
import json
import os

from gamestate import GameState
from game_config import GameConfig
from src.events.events import reveal_event

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library", "scenarios")

# Preset name -> board fill + beast list [(reel, row, direction, multiplier)] + zero flag.
PRESETS = {
    # one beast fires right across the centre row of an all-L5 board
    "single": {"fill": "L5", "beasts": [(2, 2, "right", 3)]},
    # two beasts on the centre row: their paths cross -> shared line multiplies (x2 * x3 = x6)
    "overlap": {"fill": "L5", "beasts": [(1, 2, "right", 2), (3, 2, "left", 3)]},
    # beast at the left edge facing out -> empty path (whiff); still a wild on its own cell
    "whiff": {"fill": "L5", "beasts": [(0, 2, "left", 5)]},
    # two beasts in the same row near the RIGHT edge, BOTH facing right -> only their own two
    # cells become wild (reel 4 whiffs at the edge; reel 3 reaches reel 4). NOT the whole row.
    "right-pair": {"fill": "L5", "beasts": [(3, 2, "right", 2), (4, 2, "right", 3)]},
    # --- vertical-facing beasts (fire up/down a column) ---
    # single beast at the top of the centre column facing DOWN -> fills the column downward
    "down": {"fill": "L5", "beasts": [(2, 0, "down", 3)]},
    # single beast at the bottom of the centre column facing UP -> fills the column upward
    "up": {"fill": "L5", "beasts": [(2, 4, "up", 5)]},
    # two beasts in the same column facing TOWARD each other -> their paths overlap mid-column (x2*x3=x6)
    "vertical-overlap": {"fill": "L5", "beasts": [(2, 1, "down", 2), (2, 3, "up", 3)]},
    # two beasts in the same column near the BOTTOM, BOTH facing down -> only their own two cells
    # become wild (row 4 whiffs at the edge; row 3 reaches row 4). NOT the whole column.
    "down-pair": {"fill": "L5", "beasts": [(2, 3, "down", 2), (2, 4, "down", 3)]},
    # all-H1 board + two big beasts overlapping -> blows past the 5000x cap (wincap event)
    "near-max": {"fill": "H1", "beasts": [(1, 2, "right", 50), (3, 2, "left", 50)]},
    # distinct symbol per reel, no beasts -> no line reaches 3-of-a-kind -> zero win
    "zero": {"fill": "L5", "beasts": [], "zero": True},
}


def build_scenario(fill="L5", beasts=None, zero=False):
    """Force a board + beasts, run the resolution pipeline, return book.to_json()."""
    beasts = beasts or []
    config = GameConfig()
    gs = GameState(config)
    gs.reset_seed(0)
    gs.betmode = "base"
    gs.criteria = "basegame"
    gs.reset_book()
    gs.gametype = config.basegame_type

    width = config.num_reels
    height = config.num_rows[0]

    if zero:
        cols = ["L2", "L3", "L4", "L5", "H1"]
        board = [[gs.symbol_storage.create_symbol(cols[r % len(cols)]) for _ in range(height)] for r in range(width)]
    else:
        board = [[gs.symbol_storage.create_symbol(fill) for _ in range(height)] for r in range(width)]

    forced_beasts = []
    for (reel, row, direction, mult) in beasts:
        beast = gs.symbol_storage.create_symbol("WILD")
        beast.direction = direction
        beast.multiplier = None  # hidden at reveal; the forced value is applied after reveal
        board[reel][row] = beast
        forced_beasts.append((beast, int(mult)))

    gs.board = board
    pad = "L2" if zero else fill
    gs.top_symbols = [gs.symbol_storage.create_symbol(pad) for _ in range(width)]
    gs.bottom_symbols = [gs.symbol_storage.create_symbol(pad) for _ in range(width)]
    gs.reel_positions = [0] * width
    gs.padding_position = [0] * width
    gs.anticipation = [0] * width
    gs.get_special_symbols_on_board()

    # Resolution pipeline (same order as run_spin, minus reel draw / repeat / freespins).
    reveal_event(gs)  # beast direction is serialized; multiplier stays hidden
    for beast, mult in forced_beasts:
        beast.multiplier = mult  # apply the forced multiplier AFTER reveal so resolution honors it
    gs.resolve_prism_beasts()
    gs.evaluate_lines_board()
    gs.win_manager.update_gametype_wins(gs.gametype)
    gs.evaluate_finalwin()

    return gs.book.to_json()


def summarize(name, book):
    from collections import Counter

    types = Counter(e["type"] for e in book["events"])
    line_mults = []
    for e in book["events"]:
        if e["type"] == "winInfo":
            for w in e["wins"]:
                line_mults.append(w["meta"]["lineMultiplier"])
    whiffs = sum(1 for e in book["events"] if e["type"] == "prismBeast" and e.get("whiff"))
    print(
        f"  [{name}] payoutMultiplier={book['payoutMultiplier']} "
        f"({book['payoutMultiplier']/100:.2f}x)  events={dict(types)}  "
        f"lineMultipliers={sorted(set(line_mults))}  whiffs={whiffs}"
    )


def write_book(name, book):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=2)
    return path


def parse_beasts(raw):
    """raw: list of [pos, dir, mult] groups -> [(reel,row,direction,mult)]."""
    out = []
    for grp in raw:
        pos, direction, mult = grp
        reel, row = (int(x) for x in pos.split(","))
        assert direction in ("up", "down", "left", "right"), f"bad direction {direction}"
        out.append((reel, row, direction, int(mult)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Prism Path forced-outcome scenario controller")
    ap.add_argument("--preset", choices=sorted(PRESETS.keys()), help="named scenario")
    ap.add_argument(
        "--beast",
        action="append",
        nargs=3,
        metavar=("REEL,ROW", "DIR", "MULT"),
        help="force a beast, e.g. --beast 2,2 right 3 (repeatable)",
    )
    ap.add_argument("--fill", default="L5", help="board fill symbol for --beast mode (default L5)")
    ap.add_argument("--zero", action="store_true", help="build a guaranteed zero-win board")
    ap.add_argument("--name", default="custom", help="output name for --beast mode")
    ap.add_argument("--all", action="store_true", help="generate every preset into scenario_books.json")
    args = ap.parse_args()

    if args.all:
        combined = {}
        print("Generating all presets:")
        for name, spec in PRESETS.items():
            book = build_scenario(spec.get("fill", "L5"), spec.get("beasts"), spec.get("zero", False))
            combined[name] = book
            summarize(name, book)
            write_book(name, book)
        os.makedirs(OUT_DIR, exist_ok=True)
        combined_path = os.path.join(OUT_DIR, "scenario_books.json")
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2)
        print(f"\nWrote {combined_path}")
        return

    if args.preset:
        spec = PRESETS[args.preset]
        book = build_scenario(spec.get("fill", "L5"), spec.get("beasts"), spec.get("zero", False))
        summarize(args.preset, book)
        print("Wrote", write_book(args.preset, book))
        return

    if args.beast or args.zero:
        beasts = parse_beasts(args.beast) if args.beast else []
        book = build_scenario(args.fill, beasts, args.zero)
        summarize(args.name, book)
        print("Wrote", write_book(args.name, book))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
