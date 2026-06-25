"""Quick validation of the sticky free-spins feature (no full create_books / wincap repeats)."""

from gamestate import GameState
from game_config import GameConfig

gs = GameState(GameConfig())
gs.betmode = "bonus"
gs.criteria = "freegame"

for sim in range(4):
    gs.run_spin(sim)
    book = gs.book.to_json()
    reveals = [e for e in book["events"] if e["type"] == "reveal"]
    fs_trigger = [e for e in book["events"] if e["type"] == "freeSpinTrigger"]
    fs_end = [e for e in book["events"] if e["type"] == "freeSpinEnd"]
    print(f"\nsim {sim}: payoutMultiplier={book['payoutMultiplier']} ({book['payoutMultiplier']/100:.2f}x) "
          f"events={len(book['events'])} reveals={len(reveals)} fsTrigger={len(fs_trigger)} fsEnd={len(fs_end)}")
    # sticky wilds should grow across the free-spin reveals (board fills up)
    counts = []
    for rv in reveals:
        wilds = sum(1 for col in rv["board"] for cell in col if cell.get("name") == "WILD")
        counts.append((rv["gameType"], wilds))
    print("  wild-cells per reveal (gametype,count):", counts)
print("\nFREE-SPINS TEST DONE")
