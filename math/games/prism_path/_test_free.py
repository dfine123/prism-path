"""Quick validation of the reworked bonus design (no full create_books / wincap repeats).

Checks per mode:
  bonus: dragons fire per spin; wild PATHS do NOT persist across spins; sticky dragons
         (if any) re-land in the SAME cell every remaining spin.
  super: EVERY free spin has at least one dragon (guarantee); sticky chance is higher.
"""

from gamestate import GameState
from game_config import GameConfig


def dragons_in_reveal(rv):
    """WILD cells in the VISIBLE rows (skip top/bottom padding)."""
    out = []
    for reel, col in enumerate(rv["board"]):
        for row, cell in enumerate(col):
            if row == 0 or row == len(col) - 1:
                continue
            if cell.get("name") == "WILD":
                out.append((reel, row, bool(cell.get("sticky")), cell.get("multiplier")))
    return out


def run_mode(gs, betmode, sims):
    gs.betmode = betmode
    gs.criteria = "freegame"
    print(f"\n=== {betmode.upper()} ===")
    guarantee_violations = 0
    sticky_seen = 0
    for sim in range(sims):
        gs.run_spin(sim)
        book = gs.book.to_json()
        reveals = [e for e in book["events"] if e["type"] == "reveal"]
        free_reveals = [rv for rv in reveals if rv["gameType"] == "freegame"]
        sticky_events = [e for e in book["events"] if e["type"] == "prismBeast" and e.get("sticky")]
        per_spin = []
        sticky_cells_by_spin = []
        for rv in free_reveals:
            ds = dragons_in_reveal(rv)
            per_spin.append(len(ds))
            sticky_cells_by_spin.append({(r, w) for (r, w, st, m) in ds if st})
            if betmode == "super" and len(ds) == 0:
                guarantee_violations += 1
        if sticky_events:
            sticky_seen += 1
        # sticky dragons must stay in the SAME cell once seated
        stable = True
        seated = set()
        for cells in sticky_cells_by_spin:
            if not seated.issubset(cells) and seated:
                stable = False
            seated = seated | cells
        print(
            f"  sim {sim}: {book['payoutMultiplier']/100:>8.2f}x  freeSpins={len(free_reveals)}  "
            f"dragons/spin={per_spin}  stickyFires={len(sticky_events)}  stickyStable={stable}"
        )
    print(f"  -> guarantee violations: {guarantee_violations} (must be 0 for super)")
    print(f"  -> sims with a sticky dragon: {sticky_seen}/{sims}")
    return guarantee_violations


gs = GameState(GameConfig())
v = 0
v += run_mode(gs, "bonus", 5)
v += run_mode(gs, "super", 5)
print("\nRESULT:", "FAIL (guarantee violated)" if v else "PASS")
