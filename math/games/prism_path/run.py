"""Prism Path — Phase 1 run: flat odds, optimizer STUBBED.

Generates random base-game books so the feature can be felt during random play. No RTP
convergence, no weighted reelstrips, no 100k sim (those are Phase 2). With run_optimization
off, write_data auto-copies the flat lookUpTable -> lookUpTable_base_0.csv (every book weight 1).

Run from the math/ root:  python games/prism_path/run.py
Outputs land in games/prism_path/library/ (publish_files/ holds index.json + books + LUT).
"""

import glob
import os

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs


def _clear_stale_publish_artifacts():
    """Delete published lookup tables before a run.

    write_configs.make_be_config only copies the freshly generated LUT to
    publish_files/lookUpTable_<mode>_0.csv when that file does NOT already exist, so a
    second run leaves the OLD payout column published against NEW books. That tears the
    two artifacts apart (rows claiming 5000x against books that pay far less) — the RGS
    would then select by a payout table that disagrees with what the book actually pays.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    for path in glob.glob(os.path.join(here, "library", "publish_files", "lookUpTable_*.csv")):
        os.remove(path)


if __name__ == "__main__":
    _clear_stale_publish_artifacts()
    num_threads = 1            # single-thread: deterministic + the engine's safe path
    batching_size = 100000     # large -> sim counts bypass the divisibility assert
    compression = True         # produce the real books_base.jsonl.zst the RGS expects
    profiling = False

    # 100K-round sample corpus (operator direction 2026-08-04): base-dominant with
    # full feature coverage; the optimizer pass later weights these into the live LUTs.
    num_sim_args = {
        "base": int(60000),
        "bonus": int(10000),
        "super": int(10000),
        "hunt": int(10000),
        "dragon3": int(5000),
        "dragon5": int(5000),
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
