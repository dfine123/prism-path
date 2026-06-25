"""Prism Path — custom game-state overrides: Prism Beast assignment + path resolution."""

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import prism_beast_event, prism_path_event


class GameStateOverride(GameExecutables):
    """Override/extend universal state.py functions for Prism Path."""

    def reset_book(self):
        super().reset_book()

    def assign_special_sym_function(self):
        # A drawn Prism Beast faces a direction at DRAW, so it lands facing the way it will fire
        # (direction is serialized into the reveal board). Its MULTIPLIER stays hidden until it
        # travels (assigned at firing in resolve_prism_beasts).
        self.special_symbol_functions = {"WILD": [self.assign_beast_direction]}

    def assign_beast_direction(self, symbol) -> None:
        """Give a drawn beast its facing direction (revealed on the board); keep multiplier hidden."""
        symbol.direction = get_random_outcome(self.config.beast_dir_weights)
        symbol.multiplier = None

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

        # Emit events (reveal already in book). Each beast carries its OWN multiplier on every cell
        # it covers; the frontend ACCUMULATES (multiplies) as beasts pass, so an overlap cell visibly
        # grows to the product (x2 -> x6) when the second beast crosses it. prismPath is ALWAYS
        # emitted (empty cells for a whiff) so the frontend can animate: drop -> travel square-by-
        # square revealing each cell's multiplier -> transform away at the edge.
        # Per beast: drop (prismBeast) immediately followed by travel (prismPath), sequentially.
        for b in beasts_meta:
            prism_beast_event(self, b["position"], b["direction"], b["multiplier"], b["whiff"])
            # Route = own cell FIRST, then the path to the edge; each carries this beast's own
            # multiplier. The frontend replaces each covered symbol with a directional multiplier
            # wild and ACCUMULATES (a second beast over a cell multiplies it -> product).
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
