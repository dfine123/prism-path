"""Prism Path — custom game-state overrides: Prism Beast assignment + path resolution."""

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import prism_beast_event, prism_path_event


class GameStateOverride(GameExecutables):
    """Override/extend universal state.py functions for Prism Path."""

    def reset_book(self):
        super().reset_book()

    def assign_special_sym_function(self):
        # Beast multiplier + direction are assigned at FIRING time (resolve_prism_beasts), not at
        # draw — so the static reveal shows plain wilds and each beast dramatically reveals its
        # multiplier when it lands (prismBeast). No per-symbol draw-time function is needed.
        self.special_symbol_functions = {}

    # ---- Prism Path feature resolution ---------------------------------------------------

    def _beast_path_positions(self, reel: int, row: int, direction: str) -> list:
        """Cells from the beast to the grid edge in the facing direction (own cell EXCLUDED).
        A beast at the edge facing outward returns [] -> it whiffs (intended)."""
        cells = []
        height = self.config.num_rows[reel]
        width = self.config.num_reels
        if direction == "up":  # toward row 0 (top)
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

    def resolve_prism_beasts(self) -> None:
        """Fire each Prism Beast's path. Runs AFTER draw_board (reveal already emitted, showing
        the pre-path board) and BEFORE evaluate_lines_board (so line eval sees the placed wilds).

        For each beast: read its multiplier + direction, compute the path to the edge, mark the
        own cell + path cells as multiplier wilds carrying ``beast_mults = {beast_id: multiplier}``.
        Distinct beasts covering a cell stack into beast_mults; the cell's display multiplier is the
        product (matches the 'cell covered by two beasts shows the product' rule). Then emit
        prismBeast (one per beast) followed by prismPath (one per non-whiff beast).
        """
        beast_positions = list(self.special_syms_on_board.get("wild", []))
        if not beast_positions:
            return

        beast_positions = sorted(beast_positions, key=lambda p: (p["reel"], p["row"]))
        cap = self.config.max_beasts[self.gametype]
        firing = beast_positions[:cap]

        # Extras beyond the cap stay as plain wilds (no multiplier, no path).
        for p in beast_positions[cap:]:
            extra = self.board[p["reel"]][p["row"]]
            extra.multiplier = 1
            extra.direction = None

        coverage = {}  # (reel,row) -> {beast_id: multiplier}
        beasts_meta = []
        for beast_id, p in enumerate(firing):
            reel, row = p["reel"], p["row"]
            cell = self.board[reel][row]
            # Assign the beast's multiplier (MULT_SET) and facing direction at firing time.
            # If they are already set (e.g. forced by scenario.py), honor them; else roll randomly.
            mult = int(cell.multiplier) if (cell.multiplier and cell.multiplier > 1) else get_random_outcome(
                self.config.beast_mult_weights[self.gametype]
            )
            direction = cell.direction if cell.direction else get_random_outcome(self.config.beast_dir_weights)
            cell.multiplier = mult
            cell.direction = direction

            path = self._beast_path_positions(reel, row, direction)
            whiff = len(path) == 0
            for (cr, crow) in [(reel, row)] + path:
                coverage.setdefault((cr, crow), {})[beast_id] = mult
            beasts_meta.append(
                {
                    "id": beast_id,
                    "position": {"reel": reel, "row": row},
                    "direction": direction,
                    "multiplier": mult,
                    "whiff": whiff,
                    "path": path,
                }
            )

        # Convert every covered cell into a multiplier wild.
        for (cr, crow), beast_mults in coverage.items():
            cell = self.board[cr][crow]
            cell.wild = True
            cell.beast_mults = dict(beast_mults)
            product = 1
            for m in beast_mults.values():
                product *= m
            cell.multiplier = product

        # Emit events: all beasts land first, then paths sweep (reveal already in book).
        for b in beasts_meta:
            prism_beast_event(self, b["position"], b["direction"], b["multiplier"], b["whiff"])
        for b in beasts_meta:
            if b["whiff"]:
                continue
            cells = []
            for (cr, crow) in b["path"]:
                disp = 1
                for m in coverage[(cr, crow)].values():
                    disp *= m
                cells.append({"position": {"reel": cr, "row": crow}, "multiplier": disp})
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
