"""Global multipliers, symbol multipliers, combined multipliers or no actions
    All functions return [final_win_amount], [applied multiplier]"""

from typing import List, Dict
from src.calculations.board import Board


def apply_mult(
    board: Board,
    strategy: str,
    win_amount: float = 0.0,
    global_multiplier: int = 1,
    positions: list = [],
    multiplier_key: str = "multiplier",
):
    """Apply multiplier method to win_amount and winning symbol positions."""
    strat = {
        "global": apply_global_mult(win_amount, global_multiplier),
        "symbol": apply_added_symbol_mult(board, win_amount, positions, multiplier_key=multiplier_key),
        "combined": apply_combined_mult(
            board, win_amount, global_multiplier, positions, multiplier_key=multiplier_key
        ),
        # Prism Path: line win = base * product of DISTINCT intersecting beasts' multipliers.
        "prism_product": apply_prism_product_mult(board, win_amount, positions),
    }
    return strat[strategy]


def apply_prism_product_mult(board: Board, win_amount: float, positions: List[Dict], multiplier_key: str = "beast_mults") -> tuple:
    """Prism Path multiplier rule (MULT_COMBINE='product').

    Each multiplier-wild cell (a beast's own cell or any cell on its path) carries
    ``beast_mults = {beast_id: multiplier}``. A line's multiplier is the product of the
    multipliers of the DISTINCT beasts whose covered cells intersect the line's winning
    positions: one beast counts once even if it covers several winning cells, and two
    beasts on the same line MULTIPLY (the rare overlap jackpot). No beasts -> x1.
    """
    seen: Dict = {}
    for pos in positions:
        cell = board[pos["reel"]][pos["row"]]
        beast_mults = getattr(cell, multiplier_key, None)
        if beast_mults:
            for beast_id, mult in beast_mults.items():
                seen[beast_id] = mult
    product = 1
    for mult in seen.values():
        product *= mult
    # Clamp: on a saturated sticky free-spins board a line can cross many distinct beasts; the win
    # is capped at wincap anyway, so bound the product well above any meaningful value to avoid
    # float overflow / absurd display while never affecting an actual (capped) payout.
    product = min(max(product, 1), 100_000)
    return (round(win_amount * product, 2), product)


def apply_global_mult(win_amount: float, global_multiplier: int) -> tuple:
    """Enhance win global multiplier"""
    return (round(win_amount * global_multiplier, 2), global_multiplier)


def apply_added_symbol_mult(board: Board, win_amount: float, positions: List[Dict], multiplier_key: str) -> tuple:
    """Get multiplier attribute from all winning positions"""
    symbol_multiplier = 0
    for pos in positions:
        if (
            board[pos["reel"]][pos["row"]].check_attribute(multiplier_key)
            and board[pos["reel"]][pos["row"]].get_attribute(multiplier_key) > 1
        ):
            symbol_multiplier += board[pos["reel"]][pos["row"]].get_attribute(multiplier_key)
    return (round(win_amount * max(symbol_multiplier, 1), 2), max(symbol_multiplier, 1))


def apply_combined_mult(
    board: Board, win_amount: float, global_multiplier: int, positions: List[Dict], multiplier_key
) -> tuple:
    """Apply symbol multipliers and then global multiplier"""
    win, sym_mult = apply_added_symbol_mult(board, win_amount, positions, multiplier_key)
    return (win * global_multiplier  , sym_mult * global_multiplier)
