"""Verify Prism Path book output: event order, board orientation, beast cells, multiplier meta."""

import io
import json
import os
from collections import Counter

import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "library", "publish_files", "books_base.jsonl.zst")


def load_books():
    dctx = zstandard.ZstdDecompressor()
    books = []
    with open(PATH, "rb") as fh:
        reader = dctx.stream_reader(fh)
        text = io.TextIOWrapper(reader, encoding="utf-8")
        for line in text:
            line = line.strip()
            if line:
                books.append(json.loads(line))
    return books


def main():
    books = load_books()
    print("total books:", len(books))

    types = Counter()
    for b in books:
        for e in b["events"]:
            types[e["type"]] += 1
    print("event types:", dict(types))

    beasts_per_book = Counter()
    payouts = []
    for b in books:
        beasts_per_book[sum(1 for e in b["events"] if e["type"] == "prismBeast")] += 1
        payouts.append(b["payoutMultiplier"])
    print("beasts/book:", dict(sorted(beasts_per_book.items())))
    print("payoutMultiplier: min", min(payouts), "max", max(payouts), "nonzero", sum(1 for p in payouts if p > 0))

    # --- structural checks ---
    errors = []
    sample_reveal = None
    for b in books:
        evs = b["events"]
        # index sequential
        for i, e in enumerate(evs):
            if e["index"] != i:
                errors.append(f"book {b['id']}: event index {e['index']} != {i}")
                break
        # order: reveal first, finalWin last
        if evs[0]["type"] != "reveal":
            errors.append(f"book {b['id']}: first event {evs[0]['type']} != reveal")
        if evs[-1]["type"] != "finalWin":
            errors.append(f"book {b['id']}: last event {evs[-1]['type']} != finalWin")
        # beast events precede winInfo; path precede winInfo
        idx_win = next((i for i, e in enumerate(evs) if e["type"] == "winInfo"), None)
        idx_beast = [i for i, e in enumerate(evs) if e["type"] == "prismBeast"]
        idx_path = [i for i, e in enumerate(evs) if e["type"] == "prismPath"]
        if idx_win is not None:
            if idx_beast and max(idx_beast) > idx_win:
                errors.append(f"book {b['id']}: prismBeast after winInfo")
            if idx_path and max(idx_path) > idx_win:
                errors.append(f"book {b['id']}: prismPath after winInfo")
        # beasts before paths
        if idx_beast and idx_path and max(idx_beast) > min(idx_path):
            errors.append(f"book {b['id']}: a prismBeast emitted after a prismPath")
        if sample_reveal is None:
            sample_reveal = evs[0]

    # reveal orientation: [reel][row], 5 reels, 7 rows (5 + 2 padding), cells are {name}
    rv = sample_reveal
    nreel = len(rv["board"])
    nrow = len(rv["board"][0])
    print("reveal board: reels", nreel, "rows", nrow, "(expect 5 x 7 with padding)")
    if nreel != 5 or nrow != 7:
        errors.append(f"reveal board shape {nreel}x{nrow} != 5x7")
    if not isinstance(rv["board"][0][0], dict) or "name" not in rv["board"][0][0]:
        errors.append("reveal cell is not an object with 'name'")

    # beast cell name check: pick a book with a beast, confirm board cell at beast position is WILD
    checked_beast_cell = False
    for b in books:
        reveal = b["events"][0]
        beast = next((e for e in b["events"] if e["type"] == "prismBeast"), None)
        if beast:
            pos = beast["position"]  # client coords (row already +1)
            cell = reveal["board"][pos["reel"]][pos["row"]]
            if cell.get("name") != "WILD":
                errors.append(f"book {b['id']}: beast cell at {pos} is {cell.get('name')} not WILD")
            else:
                checked_beast_cell = True
            break

    # multiplier-meta check: find a winInfo where a beast multiplier was applied (lineMultiplier > 1)
    found_mult_win = None
    found_overlap = None
    for b in books:
        for e in b["events"]:
            if e["type"] == "winInfo":
                for w in e["wins"]:
                    lm = w["meta"]["lineMultiplier"]
                    if lm > 1 and found_mult_win is None:
                        found_mult_win = (b["id"], w["symbol"], lm, w["meta"]["multiplier"], w["win"], w["meta"]["winWithoutMult"])
                    # overlap: lineMultiplier that is a product of two beasts (>5 means not a single {2,3,5})
                    if lm > 5 and found_overlap is None:
                        found_overlap = (b["id"], w["symbol"], lm, w["win"], w["meta"]["winWithoutMult"])

    print("checked beast cell == WILD:", checked_beast_cell)
    print("example multiplied win (id,sym,lineMult,multiplier,win,winWithoutMult):", found_mult_win)
    print("example overlap win (lineMult>5):", found_overlap)
    # verify win == winWithoutMult * lineMultiplier for the multiplied example
    if found_mult_win:
        _id, _sym, lm, mult, win, wwm = found_mult_win
        ok = (win == wwm * lm)
        print(f"  win == winWithoutMult * lineMultiplier ? {win} == {wwm}*{lm} -> {ok}")
        if not ok:
            errors.append("multiplied win amount mismatch")

    print("\nERRORS:", len(errors))
    for e in errors[:20]:
        print("  -", e)
    print("VERIFY", "PASS" if not errors else "FAIL")


if __name__ == "__main__":
    main()
