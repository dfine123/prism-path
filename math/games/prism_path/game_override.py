"""Prism Path — custom game-state overrides: Prism Beast assignment + path resolution.

Every spin is SELF-CONTAINED: dragons fire, their wild paths pay this spin and clear.
FREE GAME: a landing dragon may become STICKY — it stays for the rest of the feature,
re-lands in the SAME cell every spin with a FRESH direction (same multiplier, its identity),
and fires a fresh path each spin. Paths never persist across spins.
SUPER buy additionally guarantees at least one dragon on every free spin (injected if the
draw holds none) and carries a higher sticky chance (config.sticky_dragon_chance).
"""

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import prism_beast_event, prism_path_event


class GameStateOverride(GameExecutables):
    """Override/extend universal state.py functions for Prism Path."""

    def reset_book(self):
        super().reset_book()
        self.sticky_dragons = []  # [{"reel","row","mult"}] — persists across FREE spins only

    def reset_prism_feature(self):
        """Clear sticky dragons at the START of a free-spins feature."""
        self.sticky_dragons = []

    def assign_special_sym_function(self):
        # A drawn Prism Beast faces a direction at DRAW (serialized into the reveal so it lands
        # facing its travel direction); its MULTIPLIER stays hidden until it fires.
        self.special_symbol_functions = {"WILD": [self.assign_beast_direction]}

    def assign_beast_direction(self, symbol) -> None:
        symbol.direction = get_random_outcome(self.config.beast_dir_weights)
        symbol.multiplier = None

    # ---- feature helpers ------------------------------------------------------------------

    def _sticky_chance(self) -> float:
        if self.gametype != self.config.freegame_type:
            return 0.0
        return float(self.config.sticky_dragon_chance.get(self.betmode, 0.0))

    def _guarantee_dragon(self) -> bool:
        if self.gametype != self.config.freegame_type:
            return False
        return bool(self.config.guarantee_dragon.get(self.betmode, False))

    def stamp_sticky_dragons(self) -> None:
        """Re-land every sticky dragon on a freshly drawn free-spin board: SAME cell, FRESH
        direction, its own multiplier (serialized in the reveal -> the client shows the
        returning dragon seated with its badge)."""
        for d in self.sticky_dragons:
            sym = self.symbol_storage.create_symbol("WILD")
            sym.direction = get_random_outcome(self.config.beast_dir_weights)
            sym.multiplier = int(d["mult"])
            sym.sticky = True
            self.board[d["reel"]][d["row"]] = sym

    def ensure_base_dragon_guarantee(self) -> None:
        """FEATURE SPINS (dragon3/dragon5): guarantee N dragons on the BASE spin. Injected
        pre-reveal at random non-scatter, non-wild cells (direction assigned; multiplier
        hidden until fire) — scatters are untouched, so the spin can still trigger the bonus
        naturally."""
        n = int(self.config.base_dragon_guarantee.get(self.betmode, 0))
        if n <= 0 or self.gametype != self.config.basegame_type:
            return
        candidates = []
        count = 0
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                cell = self.board[reel][row]
                if cell.name == "WILD":
                    count += 1
                elif cell.name != "SCAT":
                    candidates.append((reel, row))
        while count < n and candidates:
            pick = get_random_outcome({c: 1 for c in candidates})
            candidates.remove(pick)
            sym = self.symbol_storage.create_symbol("WILD")
            sym.direction = get_random_outcome(self.config.beast_dir_weights)
            sym.multiplier = None
            self.board[pick[0]][pick[1]] = sym
            count += 1

    def ensure_dragon_guarantee(self) -> None:
        """SUPER: if the board holds no dragon at all after the draw (+sticky stamp), inject
        one at a random non-scatter cell (direction assigned; multiplier hidden until fire)."""
        if not self._guarantee_dragon():
            return
        candidates = {}
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                cell = self.board[reel][row]
                if cell.name == "WILD":
                    return  # guarantee already satisfied
                if cell.name != "SCAT":
                    candidates[(reel, row)] = 1
        reel, row = get_random_outcome(candidates)
        sym = self.symbol_storage.create_symbol("WILD")
        sym.direction = get_random_outcome(self.config.beast_dir_weights)
        sym.multiplier = None
        self.board[reel][row] = sym

    # ---- Prism Path feature resolution ------------------------------------------------------

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

    def resolve_prism_beasts(self) -> None:
        """Fire EVERY dragon on the board (never drop one — an un-fired dragon renders as a
        stuck beast). Per-spin coverage only.

        Sticky dragons keep their multiplier and STAY seated: their own cell is a wild
        carrying their multiplier, and their prismPath cells EXCLUDE the own cell so the
        client leaves the dragon in place. New dragons roll a multiplier; in the free game
        they may become sticky (capped at config.max_sticky_dragons). Distinct dragons
        crossing on a cell multiply (per-beast-once product via beast_mults).
        """
        self.get_special_symbols_on_board()  # refresh after sticky stamp / guarantee injection
        all_wilds = sorted(
            self.special_syms_on_board.get("wild", []), key=lambda p: (p["reel"], p["row"])
        )
        if not all_wilds:
            return

        sticky_pos = {(d["reel"], d["row"]): d for d in self.sticky_dragons}
        coverage = {}  # (reel,row) -> {"beast_mults": {id: mult}, "direction": str, "sticky": bool}
        beasts_meta = []
        beast_id = 0
        for p in all_wilds:
            reel, row = p["reel"], p["row"]
            cell = self.board[reel][row]
            returning = sticky_pos.get((reel, row))
            if returning is not None:
                mult = int(returning["mult"])
                is_sticky = True
            else:
                mult = int(cell.multiplier) if (cell.multiplier and cell.multiplier > 1) else get_random_outcome(
                    self.config.beast_mult_weights[self.gametype]
                )
                is_sticky = False
                chance = self._sticky_chance()
                if chance > 0 and len(self.sticky_dragons) < self.config.max_sticky_dragons:
                    if get_random_outcome({True: chance, False: 1.0 - chance}):
                        self.sticky_dragons.append({"reel": reel, "row": row, "mult": mult})
                        sticky_pos[(reel, row)] = self.sticky_dragons[-1]
                        is_sticky = True

            direction = cell.direction if cell.direction else get_random_outcome(self.config.beast_dir_weights)
            cell.direction = direction
            cell.multiplier = mult

            path = self._beast_path_positions(reel, row, direction)
            whiff = len(path) == 0
            for (cr, crow) in [(reel, row)] + path:
                entry = coverage.setdefault(
                    (cr, crow), {"beast_mults": {}, "direction": direction, "sticky": False}
                )
                entry["beast_mults"][beast_id] = mult
            coverage[(reel, row)]["sticky"] = is_sticky
            coverage[(reel, row)]["direction"] = direction
            beasts_meta.append(
                {
                    "position": {"reel": reel, "row": row},
                    "direction": direction,
                    "multiplier": mult,
                    "whiff": whiff,
                    "path": path,
                    "sticky": is_sticky,
                }
            )
            beast_id += 1

        # write the per-spin coverage onto the board for line evaluation
        for (reel, row), entry in coverage.items():
            product = 1
            for m in entry["beast_mults"].values():
                product *= m
            sym = self.symbol_storage.create_symbol("WILD")
            sym.wild = True
            sym.beast_mults = dict(entry["beast_mults"])
            sym.multiplier = product
            sym.direction = entry["direction"]
            sym.sticky = entry["sticky"]
            self.board[reel][row] = sym

        # events: per dragon, drop (prismBeast) then travel (prismPath). EVERY dragon (sticky
        # included) animates the full travel — the route includes its own cell, which converts
        # to a trail wild as it departs. Stickiness is signalled client-side by a persistent
        # glowing border on the landing square (the dragon re-lands there next spin).
        for b in beasts_meta:
            prism_beast_event(
                self, b["position"], b["direction"], b["multiplier"], b["whiff"], sticky=b["sticky"]
            )
            route = [b["position"]] + [{"reel": cr, "row": crow} for (cr, crow) in b["path"]]
            cells = [{"position": pos, "multiplier": b["multiplier"]} for pos in route]
            prism_path_event(
                self, b["position"], b["direction"], cells, sticky=b["sticky"], multiplier=b["multiplier"]
            )

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
