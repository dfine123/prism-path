"""Prism Path — custom game-state overrides: Prism Beast assignment + path resolution.

Base game: beasts fire once per spin (sticky_cells reset each spin).
Free game: beasts (and the multiplier wilds they leave) are STICKY — sticky_cells + a feature-wide
beast-id counter persist across spins, so new beasts overlap-multiply prior wilds (per-beast-once,
distinct beasts multiply) and the board fills up over the feature.
"""

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import prism_beast_event, prism_path_event


class GameStateOverride(GameExecutables):
    """Override/extend universal state.py functions for Prism Path."""

    def reset_book(self):
        super().reset_book()
        # per base-round prism state (free game re-resets these once at feature start)
        self.next_beast_id = 0
        self.sticky_cells = {}  # (reel,row) -> {"beast_mults": {id: mult}, "direction": str}

    def reset_prism_feature(self):
        """Clear sticky wilds + beast ids at the START of a free-spins feature."""
        self.next_beast_id = 0
        self.sticky_cells = {}

    def assign_special_sym_function(self):
        # A drawn Prism Beast faces a direction at DRAW (serialized into the reveal so it lands
        # facing its travel direction); its MULTIPLIER stays hidden until it fires.
        self.special_symbol_functions = {"WILD": [self.assign_beast_direction]}

    def assign_beast_direction(self, symbol) -> None:
        symbol.direction = get_random_outcome(self.config.beast_dir_weights)
        symbol.multiplier = None

    # ---- Prism Path feature resolution ---------------------------------------------------

    def _beast_path_positions(self, reel: int, row: int, direction: str) -> list:
        """Cells from the beast to the grid edge in the facing direction (own cell EXCLUDED).
        A beast at the edge facing outward returns [] -> it whiffs (intended)."""
        cells = []
        height = self.config.num_rows[reel]
        width = self.config.num_reels
        if direction == "up":
            for r in range(row - 1, -1, -1):
                cells.append((reel, r))
        elif direction == "down":
            for r in range(row + 1, height):
                cells.append((reel, r))
        elif direction == "left":
            for c in range(reel - 1, -1, -1):
                cells.append((c, row))
        elif direction == "right":
            for c in range(reel + 1, width):
                cells.append((c, row))
        return cells

    def _write_sticky_to_board(self) -> None:
        """Stamp every accumulated sticky cell onto the current board as an actual WILD symbol whose
        displayed multiplier is the PRODUCT of the distinct beasts covering it (so it renders as a
        directional wild, not the underlying symbol)."""
        for (reel, row), entry in self.sticky_cells.items():
            product = 1
            for m in entry["beast_mults"].values():
                product *= m
            wild_sym = self.symbol_storage.create_symbol("WILD")
            wild_sym.wild = True
            wild_sym.beast_mults = dict(entry["beast_mults"])
            wild_sym.multiplier = product
            wild_sym.direction = entry.get("direction")
            self.board[reel][row] = wild_sym

    def apply_sticky_cells(self) -> None:
        """Re-apply prior sticky wilds onto a freshly drawn (free-spin) board so they persist."""
        self._write_sticky_to_board()

    def resolve_prism_beasts(self) -> None:
        """Fire newly-drawn Prism Beasts. Runs after the board is drawn and before line eval.

        Newly drawn beasts (special_syms_on_board['wild']) fire up to the per-gametype cap; each gets
        a feature-unique id, a multiplier (MULT_SET) and a direction, and covers its own cell + path
        to the edge. Coverage MERGES into sticky_cells (so prior sticky beasts + new beasts on a cell
        stack by distinct id -> product), then the whole accumulated state is written to the board.
        """
        beast_positions = list(self.special_syms_on_board.get("wild", []))
        if not beast_positions:
            # still ensure any sticky wilds are on the board (free game re-draws)
            self._write_sticky_to_board()
            return

        beast_positions = sorted(beast_positions, key=lambda p: (p["reel"], p["row"]))
        cap = self.config.max_beasts[self.gametype]
        firing = beast_positions[:cap]

        for p in beast_positions[cap:]:  # extras beyond cap -> plain wild (no mult / no path)
            extra = self.board[p["reel"]][p["row"]]
            extra.multiplier = 1
            extra.direction = None

        beasts_meta = []
        for p in firing:
            reel, row = p["reel"], p["row"]
            cell = self.board[reel][row]
            mult = int(cell.multiplier) if (cell.multiplier and cell.multiplier > 1) else get_random_outcome(
                self.config.beast_mult_weights[self.gametype]
            )
            direction = cell.direction if cell.direction else get_random_outcome(self.config.beast_dir_weights)
            cell.multiplier = mult
            cell.direction = direction

            beast_id = self.next_beast_id
            self.next_beast_id += 1
            path = self._beast_path_positions(reel, row, direction)
            whiff = len(path) == 0
            for (cr, crow) in [(reel, row)] + path:
                entry = self.sticky_cells.setdefault((cr, crow), {"beast_mults": {}, "direction": None})
                entry["beast_mults"][beast_id] = mult
            # own cell carries this beast's facing direction for the bust
            self.sticky_cells[(reel, row)]["direction"] = direction
            beasts_meta.append(
                {"position": {"reel": reel, "row": row}, "direction": direction, "multiplier": mult, "whiff": whiff, "path": path}
            )

        # write the full accumulated state (sticky + new) onto the board for line evaluation
        self._write_sticky_to_board()

        # Emit per new beast: drop (prismBeast) then travel (prismPath = own cell first, then path).
        for b in beasts_meta:
            prism_beast_event(self, b["position"], b["direction"], b["multiplier"], b["whiff"])
            route = [b["position"]] + [{"reel": cr, "row": crow} for (cr, crow) in b["path"]]
            cells = [{"position": pos, "multiplier": b["multiplier"]} for pos in route]
            prism_path_event(self, b["position"], b["direction"], cells)

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return
