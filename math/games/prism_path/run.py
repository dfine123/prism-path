"""Prism Path — Phase 1 run: flat odds, optimizer STUBBED.

Generates random base-game books so the feature can be felt during random play. No RTP
convergence, no weighted reelstrips, no 100k sim (those are Phase 2). With run_optimization
off, write_data auto-copies the flat lookUpTable -> lookUpTable_base_0.csv (every book weight 1).

Run from the math/ root:  python games/prism_path/run.py
Outputs land in games/prism_path/library/ (publish_files/ holds index.json + books + LUT).
"""

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    num_threads = 1            # single-thread: avoids Windows multiprocessing quirks
    batching_size = 50000      # large -> small sim counts bypass the divisibility assert
    compression = True         # produce the real books_base.jsonl.zst the RGS expects
    profiling = False

    num_sim_args = {
        "base": int(2000),     # Phase 1: small; correctness, not RTP
    }

    config = GameConfig()
    gamestate = GameState(config)

    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )
    generate_configs(gamestate)
    print("PRISM PATH RUN DONE (optimizer stubbed, flat odds)")
