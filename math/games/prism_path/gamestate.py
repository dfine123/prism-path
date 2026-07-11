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
        # FREE SPINS: per-spin dragons; STICKY DRAGONS persist. Each spin: fresh board, sticky
        # dragons re-land in their cells (fresh direction, same multiplier), SUPER guarantees at
        # least one dragon, reveal, then every dragon fires a fresh path (paths pay this spin
        # only and never persist).
        self.reset_fs_spin()
        self.reset_prism_feature()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board(emit_event=False)   # draw new symbols; defer the reveal
            self.stamp_sticky_dragons()         # returning sticky dragons land in their cells
            self.ensure_dragon_guarantee()      # SUPER: at least one dragon every spin
            reveal_event(self)                  # reveal = new symbols + seated sticky dragons
            self.resolve_prism_beasts()         # every dragon fires its path for THIS spin

            self.evaluate_lines_board()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()
