"""Prism Path — game configuration (inherits src/config/config.py).

5x5 board, 40 lines. Signature feature: the rare Prism Beast wild (symbol ``WILD``)
lands facing a random direction and fires a path of multiplier-wilds to the board edge.
When two beasts touch the same winning line their multipliers MULTIPLY.

PHASE 1: flat/placeholder reels, optimizer stubbed. RTP is NOT tuned here.
"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


# Paytable placeholders in payoutMultiplier-int units (800 = 8.0x), per the build spec.
# L1-L5 = [3,4,5]-of-a-kind -> [25,50,100]; H1-H4 -> [50,150,500]. WILD has NO own pay.
PAYTABLE_PM = {
    "L1": [25, 50, 100],
    "L2": [25, 50, 100],
    "L3": [25, 50, 100],
    "L4": [25, 50, 100],
    "L5": [25, 50, 100],
    "H1": [50, 150, 500],
    "H2": [50, 150, 500],
    "H3": [50, 150, 500],
    "H4": [50, 150, 500],
}

# 40 distinct paylines over a 5x5 grid (row indices 0..4 per reel), left-to-right.
PAYLINES_40 = [
    [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [2, 2, 2, 2, 2], [3, 3, 3, 3, 3], [4, 4, 4, 4, 4],
    [0, 1, 2, 3, 4], [4, 3, 2, 1, 0], [0, 1, 2, 1, 0], [4, 3, 2, 3, 4], [1, 2, 3, 2, 1],
    [3, 2, 1, 2, 3], [0, 0, 1, 0, 0], [4, 4, 3, 4, 4], [1, 1, 2, 1, 1], [3, 3, 2, 3, 3],
    [2, 2, 1, 2, 2], [2, 2, 3, 2, 2], [0, 1, 0, 1, 0], [4, 3, 4, 3, 4], [1, 0, 1, 0, 1],
    [3, 4, 3, 4, 3], [0, 2, 4, 2, 0], [4, 2, 0, 2, 4], [1, 2, 1, 2, 1], [3, 2, 3, 2, 3],
    [0, 0, 2, 0, 0], [4, 4, 2, 4, 4], [2, 1, 0, 1, 2], [2, 3, 4, 3, 2], [0, 1, 1, 1, 0],
    [4, 3, 3, 3, 4], [1, 1, 0, 1, 1], [3, 3, 4, 3, 3], [0, 2, 0, 2, 0], [4, 2, 4, 2, 4],
    [1, 3, 1, 3, 1], [3, 1, 3, 1, 3], [2, 0, 2, 0, 2], [2, 4, 2, 4, 2], [0, 4, 0, 4, 0],
]


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "prism_path"
        self.provider_number = 0
        self.working_name = "Prism Path"
        self.wincap = 5000.0
        self.win_type = "lines"
        self.rtp = 0.9600  # target only; NOT tuned in Phase 1 (optimizer stubbed)
        self.construct_paths()

        # Board dimensions: 5x5
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels

        # Paytable (kind, symbol) -> x-multiplier. payoutMultiplier int / 100.
        self.paytable = {}
        for sym, vals in PAYTABLE_PM.items():
            for kind, pm in zip((3, 4, 5), vals):
                self.paytable[(kind, sym)] = pm / 100.0
        # WILD (Prism Beast) carries multipliers but has NO own-symbol payout.

        # 40 paylines, keyed 1..40
        assert len({tuple(line) for line in PAYLINES_40}) == 40, "paylines must be 40 unique lines"
        self.paylines = {i + 1: list(line) for i, line in enumerate(PAYLINES_40)}

        self.include_padding = True
        # WILD = Prism Beast (wild; carries a multiplier via beast_mults set at firing — NOT the
        # "multiplier" special-flag, so it shows no multiplier on the board until it travels).
        # SCAT = scatter (free spins, deferred).
        self.special_symbols = {"wild": ["WILD"], "scatter": ["SCAT"]}

        # ---- Prism Path feature tuning (resolver reads these) ----
        self.mult_combine = "product"  # overlap multiplies the lane
        self.beast_dir_weights = {"up": 1, "down": 1, "left": 1, "right": 1}
        # MULT_SET base {2,3,5}; free spins add 10 (deferred build).
        self.beast_mult_weights = {
            self.basegame_type: {2: 5, 3: 3, 5: 2},
            self.freegame_type: {2: 5, 3: 3, 5: 2, 10: 1},
        }
        self.max_beasts = {self.basegame_type: 2, self.freegame_type: 4}

        # Free spins (DEFINED; build deferred to Phase 2)
        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 15},
            self.freegame_type: {2: 3, 3: 5, 4: 8, 5: 12},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # Reels (flat/placeholder for Phase 1)
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        # Multiplier value spread for the WILD (used by analysis/optimizer; resolver uses beast_mult_weights).
        self.padding_symbol_values = {"WILD": {"multiplier": {2: 100, 3: 50, 5: 50, 10: 30}}}

        base_conditions = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: {1: 1}},
            "force_wincap": False,
            "force_freegame": False,
        }

        mode_maxwins = {"base": 5000}
        # Phase-1 distributions: a controllable mix of forced-zero and winning base spins.
        # No wincap/freegame forcing here — beasts arise naturally from the reels; the
        # scenario controller (scenario.py) is used for precise forced outcomes.
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=base_conditions),
                    Distribution(criteria="basegame", quota=0.6, conditions=base_conditions),
                ],
            ),
        ]
