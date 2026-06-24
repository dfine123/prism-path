from game_calculations import GameCalculations
from src.calculations.lines import Lines


class GameExecutables(GameCalculations):

    def evaluate_lines_board(self):
        """Populate win-data using the Prism Path product-multiplier rule, record, transmit events.

        Uses ``multiplier_method="prism_product"``: a line's multiplier is the product of the
        DISTINCT beasts whose covered cells intersect the line's winning positions (per-beast-once,
        overlap multiplies). wild_sym="WILD" — the beast has no own paytable entry, so wild-only
        lines pay 0; wilds only substitute for L/H symbols.
        """
        self.win_data = Lines.get_lines(
            self.board,
            self.config,
            wild_key="wild",
            wild_sym="WILD",
            multiplier_method="prism_product",
            global_multiplier=self.global_multiplier,
        )
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)
