"""Prism Path — game configuration (inherits src/config/config.py).

5x5 board, 40 lines. Signature feature: the rare Prism Beast wild (symbol ``WILD``) lands
facing a random direction and fires a path of multiplier-wilds to the board edge. Two beasts
touching the same winning line MULTIPLY (per-beast-once, overlap = product) — FROZEN rule.

Modes: base + free spins (STICKY beasts/wilds) + Buy Bonus + a premium "Super" buy.
RTP is tuned at the final generation (optimizer); the values here are the model + guides.
"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


# Paytable in payoutMultiplier-int units (800 = 8.0x). L2-L5 [3,4,5] -> [25,50,100];
# H1-H4 -> [50,150,500]. WILD has NO own-symbol pay (substitutes + carries multipliers).
PAYTABLE_PM = {
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
        self.rtp = 0.9650  # guide; final RTP set by the optimizer at submission generation
        self.construct_paths()

        # Board dimensions: 5x5
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels

        # Paytable (kind, symbol) -> x-multiplier (payoutMultiplier int / 100).
        self.paytable = {}
        for sym, vals in PAYTABLE_PM.items():
            for kind, pm in zip((3, 4, 5), vals):
                self.paytable[(kind, sym)] = pm / 100.0

        # 40 paylines, keyed 1..40
        assert len({tuple(line) for line in PAYLINES_40}) == 40, "paylines must be 40 unique lines"
        self.paylines = {i + 1: list(line) for i, line in enumerate(PAYLINES_40)}

        self.include_padding = True
        # WILD = Prism Beast (wild; carries a multiplier via beast_mults, not the multiplier flag).
        self.special_symbols = {"wild": ["WILD"], "scatter": ["SCAT"]}

        # ---- Prism Path feature tuning (resolver reads these) ----
        self.mult_combine = "product"  # overlap multiplies the lane (per-beast-once)
        self.beast_dir_weights = {"up": 1, "down": 1, "left": 1, "right": 1}
        # MULT_SET base {2,3,5}; free spins add 10 (bigger beasts).
        self.beast_mult_weights = {
            self.basegame_type: {2: 5, 3: 3, 5: 2},
            self.freegame_type: {2: 10, 3: 3, 5: 1, 10: 1},  # mostly x2 so the sticky fill escalates gradually
        }
        self.max_beasts = {self.basegame_type: 2, self.freegame_type: 3}
        # FREE-SPINS HOOK: beasts (and the multiplier wilds they leave) are STICKY — they persist
        # across the feature and new beasts overlap-multiply them as the board fills.
        self.sticky_wilds_in_freegame = True

        # Free spins: scatter count -> number of spins.
        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 15},
            self.freegame_type: {3: 5, 4: 8, 5: 12},  # retrigger needs 3+ scatters (rare in free)
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # Reels: BR0 base, FR0 free (free has more beasts/scatters). WCAP not separate yet.
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        self.padding_symbol_values = {"WILD": {"multiplier": {2: 100, 3: 50, 5: 50, 10: 30}}}

        # ---- Distribution conditions (criteria setup for create_books / optimizer) ----
        reels_both = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1}}
        mults_noop = {self.basegame_type: {1: 1}, self.freegame_type: {1: 1}}

        base_conditions = {
            "reel_weights": reels_both,
            "mult_values": mults_noop,
            "force_wincap": False,
            "force_freegame": False,
        }
        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": mults_noop,
            "force_wincap": False,
            "force_freegame": False,
        }
        freegame_condition = {
            "reel_weights": reels_both,
            "mult_values": mults_noop,
            "scatter_triggers": {3: 50, 4: 20, 5: 5},
            "force_wincap": False,
            "force_freegame": True,
        }
        # Super buy = premium entry: mostly 4-5 scatters (more spins).
        super_condition = {
            "reel_weights": reels_both,
            "mult_values": mults_noop,
            "scatter_triggers": {4: 30, 5: 20},
            "force_wincap": False,
            "force_freegame": True,
        }
        wincap_condition = {
            "reel_weights": reels_both,
            "mult_values": mults_noop,
            "scatter_triggers": {4: 10, 5: 10},
            "force_wincap": True,
            "force_freegame": True,
        }

        max_win = self.wincap
        self.bet_modes = [
            # Base game: natural play; can trigger free spins from scatters.
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=max_win,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(criteria="wincap", quota=0.005, win_criteria=max_win, conditions=wincap_condition),
                    Distribution(criteria="freegame", quota=0.10, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.40, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.495, conditions=base_conditions),
                ],
            ),
            # Buy Bonus: pay to enter free spins (standard scatter distribution).
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=max_win,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(criteria="wincap", quota=0.01, win_criteria=max_win, conditions=wincap_condition),
                    Distribution(criteria="freegame", quota=0.99, conditions=freegame_condition),
                ],
            ),
            # Super buy: premium price, better entry (more scatters -> more spins).
            BetMode(
                name="super",
                cost=300.0,
                rtp=self.rtp,
                max_win=max_win,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(criteria="wincap", quota=0.02, win_criteria=max_win, conditions=wincap_condition),
                    Distribution(criteria="freegame", quota=0.98, conditions=super_condition),
                ],
            ),
        ]
