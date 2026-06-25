from game_override import GameStateOverride
from src.events.events import reveal_event


class GameState(GameStateOverride):
    """Handles game logic and events for a single Prism Path round."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()              # draws board + emits reveal (beasts face their direction)
            self.resolve_prism_beasts()    # fire beast paths -> wilds; emit prismBeast/prismPath

            # Evaluate wins (product multiplier), update wallet, transmit win events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()
        self.imprint_wins()

    def run_freespin(self):
        # FREE SPINS: beasts/wilds are STICKY. Clear the feature state once, then each spin draw a
        # fresh board, re-stamp the accumulated sticky wilds onto it, reveal, fire new beasts (which
        # overlap-multiply the sticky wilds), and evaluate. The board fills over the feature.
        self.reset_fs_spin()
        self.reset_prism_feature()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board(emit_event=False)   # draw new symbols; defer the reveal
            self.apply_sticky_cells()           # re-apply prior sticky wilds onto the new board
            reveal_event(self)                  # reveal = new symbols + accumulated sticky wilds
            self.resolve_prism_beasts()         # new beasts fire + merge into the sticky board

            self.evaluate_lines_board()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()
