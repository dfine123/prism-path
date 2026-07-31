# Prism Path — Project Context & Session Handoff

> Living handoff doc. Everything a fresh session (human or agent) needs to pick this project
> up exactly where it left off. Last updated: **2026-07-12** (commit `1b3bd6a`).

---

## 1. What this game is

**Prism Path** — a Stake Engine slot. **5 reels × 5 rows, 15 fixed paylines** (lines pay,
left-to-right). RTP target 96.5% (NOT yet tuned), win cap **5,000×**.

**Signature mechanic — the Prism Dragon (WILD):** a rare dragon lands facing a random
direction (up/down/left/right) and **fires a path of multiplier wilds** (×2/×3/×5, up to ×10
in free spins) from its square to the board edge. A dragon facing the edge whiffs off the
board. **Crossing dragon paths MULTIPLY** (per-beast-once: each dragon counts once per line;
two dragons on a line = product, ×2·×3 = ×6). A run of only wilds pays at gem tier — but a
symbol that completes a wild run **always registers the full line** (4 wilds + K = 5-line K).

**Modes:**
- **BASE** (1×) — natural play, scatters trigger free spins (3/4/5 → 8/12/15 spins;
  retrigger in-feature 3/4/5 → +5/+8/+12).
- **DRAGON BONUS** (buy, 100×) — free spins with enhanced dragon density.
- **SUPER DRAGON BONUS** (buy, 300×) — a dragon is **GUARANTEED every spin** + much higher
  **sticky-dragon** chance. (Priced provisionally; tune later.)

**Sticky dragon:** stays for the whole feature, re-lands in the SAME cell every spin with a
FRESH direction (keeps its multiplier = its identity), fires a fresh path each spin. Paths
never persist across spins. Signalled by a glowing border on its claimed square + a
dedicated crowned-dragon symbol (`WILDSTICKY`); its badge sits at the cell's bottom edge.

---

## 2. Repo layout

```
prism-path/
  math/       fork of StakeEngine math-sdk (Python). Game: math/games/prism_path/
              venv at math/env. Run everything from math/ root.
  frontend/   fork of StakeEngine web-sdk (pnpm monorepo, Svelte 5 + PixiJS 8 + XState).
              Game app: frontend/apps/prism-path/
```

**Book-driven architecture (Stake rule):** math generates ALL outcomes into books
(`index.json` + `books_<mode>.jsonl.zst` + lookup tables); the frontend only choreographs
book events. No outcome-affecting RNG client-side. Amounts are ×100 ints (100 = $1).

### Key math files (math/games/prism_path/)
- `game_config.py` — board, PAYTABLE_PM (WILD/H at [50,150,500]=0.5/1.5/5×, L at
  [25,50,100]), PAYLINES_15, bet modes/distributions, `sticky_dragon_chance`
  {base/bonus 0.15, super 0.35}, `guarantee_dragon` {super}, `max_sticky_dragons 2`,
  `beast_mult_weights`, freespin triggers.
- `game_override.py` — the resolver: `resolve_prism_beasts` (EVERY wild fires — no cap),
  `stamp_sticky_dragons`, `ensure_dragon_guarantee`, path geometry, per-spin coverage with
  `beast_mults` per cell.
- `gamestate.py` — run_spin / run_freespin flow.
- `game_executables.py` — Lines.get_lines wiring (wild_sym="WILD", prism_product strategy).
- `run.py` — generate books (optimizer STUBBED; small counts: 2000/800/800).
- **`validate_books.py` — THE AUDIT GATE.** Rendering invariants + **independent win
  re-evaluation** of every spin in every book (rebuilds board + per-beast coverage from
  events, re-scores all 17 lines, win-cap aware). Run after every `run.py`. Must be 3600/0.
- `_test_free.py` — bonus/super sanity harness (guarantee violations, sticky stability).
- `_extract_story_books.py` — samples real books into frontend story data (base 400 /
  bonus 120 / super 80).
- `scenario.py --all` — forced-outcome books for storybook scenarios (copy the JSON output
  to `frontend/apps/prism-path/src/stories/data/scenarios/` after regen).
- Framework edits: `src/calculations/lines.py` (wild-completion rule), `symbol.py`
  (+direction/beast_mults/sticky slots), `src/events/events.py` (prismBeast/prismPath events
  +sticky+multiplier; reveal serializes direction/multiplier/sticky),
  `src/wins/multiplier_strategy.py` (apply_prism_product_mult, clamp 100k).

### Key frontend files (frontend/apps/prism-path/src/)
- `game/constants.ts` — SYMBOL_SIZE 96 (cell height + square symbol size), **CELL_W =
  96·1.2155 ≈ 116.7 (cells are LANDSCAPE rectangles matching the crystal frame's opening)**,
  size-tier ratios (lows 0.72 < gems 0.88 < specials 0.94).
- `game/motion.ts` — EASE/DUR tokens + PRISM_TINTS + paletteAt/lerpColor (single source).
- `game/trailBeam.ts` — **THE shared wild-path beam renderer** (flight ribbon AND resting
  trail cells draw with this; never fork the two).
- `game/trailClock.svelte.ts` — shared refcounted rAF clock for ambient animation.
- `game/stateFx.svelte.ts` — `winSpeed` (click-to-skip multiplies presentation clocks).
- `game/stateDev.svelte.ts` + `components/DevFramePanel.svelte` — DEV frame picker
  (crystal v2 locked as boot default; REMOVE panel + losing candidates once confirmed).
- `game/betModeMeta.ts` — buy-modal cards + RGS mode strings (BASE/BONUS/SUPER).
- `components/` — PrismBeastTravel (one-continuous-motion flight), WildTrailSymbol,
  WinLines (sweep + value/multiplier popup), WinBox (layered big-win light show),
  PrismShards, PrismPanel, FreeSpinIntro/Counter/Outro, TransitionAnimation (band wipe with
  `onCovered` — bg swaps under cover), Background + BackgroundParticles (bokeh motes),
  StickyDragonMarkers, Anticipation (prism column), LoadingScreen, BoardFrame.
- Paytable/rules content: snippets in `components/Game.svelte` (payTable/gameRules) — MUST
  mirror game_config.py.

---

## 3. Commands

```bash
# math (run from math/):
env/Scripts/python.exe games/prism_path/run.py                    # generate books
env/Scripts/python.exe games/prism_path/validate_books.py         # AUDIT GATE (must pass)
env/Scripts/python.exe games/prism_path/check_feature_invariants.py # FEATURE GATE (sticky/scatter/beast contract, must pass)
env/Scripts/python.exe games/prism_path/_extract_story_books.py   # refresh story data
env/Scripts/python.exe games/prism_path/scenario.py --all         # forced scenarios
# then: cp math/games/prism_path/library/scenarios/*.json \
#          frontend/apps/prism-path/src/stories/data/scenarios/

# frontend (run from frontend/):
pnpm --filter prism-path run storybook:win     # storybook on :6010 (Windows-safe script)
```
Storybook stories: MODE_PRISM → "Play base game (random win)", "Play bonus free spins",
"Play SUPER bonus", plus forced scenarios (single/overlap/whiff/near-max/…).

---

## 4. State: everything DONE except…

The game is at **3-star final-polish state**. All template visuals replaced (generated art +
code-drawn FX), all mechanics implemented, audit gate green (3,600 books / 0 violations).

**Explicitly REMAINING (agreed scope):**
1. **Final math corpus** — optimizer run / RTP convergence to 96.5%. Current raw RTPs are
   HIGH (base ~0.94 uncapped-scale internal; buys over-value) — pricing/tuning deferred.
2. **Sound design** — template audio cues remain as functional placeholders.
3. **Frame confirmation cleanup** — crystal v2 is the boot frame; once confirmed, remove
   DevFramePanel, stateDev, and the 3 losing frame candidates (`board2-4.png`,
   `prismFrameEdge`).
4. **User visual passes** — portrait/landscape layout eyeball check; WebGPU canvas can't be
   screenshotted by the agent (known limitation — verify in a real browser).
5. **Payline set sign-off** — the 15 shapes were decoded from a low-res reference image
   (already corrected once: zigzags hug top/bottom rows). Confirm against the original.

---

## 5. Hard-won lessons (do not relearn these)

- **One renderer per visual concept.** The flight ribbon and resting trail cells MUST share
  `trailBeam.ts` (same clock, same per-cell gradient space) or the hand-off pops.
- **One motion = one curve over one path.** Never chain eased segments (windup→travel→exit
  read as stitched pauses). The dragon flies `p = u^1.35` over seat→cells→off-board.
- **Never step-change a visual property** — tween toward targets (trail win boost, badges).
- **Board lattice**: symbols at exact `(i+0.5)·CELL_W`; grid/frame share the same origin
  (the template's 0.53 padding + 1.01 position fudges caused off-center symbols).
- **Symbol textures**: alpha-CENTROID centering + uniform box fit (sparkle outliers skew
  bbox centers); value hierarchy via per-tier render ratios, not per-texture size.
- **Wild evaluator**: `lines.py` — completing symbol beats wild-run (user rule);
  pure-wild pay only when nothing completes.
- **Win-cap semantics in the validator**: recorded spin totals may be clamped once the round
  crosses 5,000×; a cap-crossing book must pay exactly 500000.
- **Click-to-skip pattern**: `stateFx.winSpeed` + scaled-time accumulation
  (`el += dt·speed`) in every paced rAF; spins slam via window pointerdown →
  `stopButtonClick` (anticipation was template-locked with `noStop` — unlocked in
  `createEnhanceBoardSpin`, spinType still 'anticipated' so pacing stays).
- **Particles**: painterly = TEXTURES (gaussian orb + star glint sprites), never flat
  Graphics circles.
- **pixi-svelte Graphics reactive-redraw**: the draw closure re-runs when $state read inside
  it changes — the pattern powering every per-frame Graphics animation here.
- **Assets**: generated art goes through download → key (white→alpha) → normalize →
  register in assets.ts. Provenance raws in `static/assets/_generated_src/`. Font "Prism" =
  Lilita One (OFL, license shipped); family name derives from the FILENAME (prism.ttf).
- **RGS mode strings**: client sends uppercase keys (BASE/BONUS/SUPER) vs lowercase math
  mode names — template convention, works.
- **Sticky flags**: reveal serializes `sticky`; frontend renders WILDSTICKY symbol; the
  glowing border marker is the claim signal (markers add on sticky prismBeast, clear on
  base reveal / freeSpinEnd).

---

## 6. Session history (chronological, by commit theme)

1. Phase 1: forks, 5×5 board, beast resolver, product multiplier, events, storybook feel
   test (overlap ×6 verified, WIN $149).
2. Real art import (SVG embedded-raster extraction), directional beast busts.
3. 3-star build: bet modes, sticky feature v1 (sticky wild PATHS — later replaced), art
   pipeline (scatter, "10" later removed, background, jewel frame, logo).
4. Layout fixes (board fit, grey grid backing), varied-gameplay stories, stuck-beast bug →
   first validator.
5. Fluid dragon animation (travel → trail v2 gradient ribbon → trail v3 per-cell beams).
6. Prism font (Lilita One) everywhere, black+white stroke.
7. Win lines (sweep, breath, value popup, multiplier merge), 15-line swap.
8. **Bonus rework**: per-spin paths only; bonus=enhanced dragons, super=guaranteed dragon +
   sticky dragons (same-cell re-land, fresh direction).
9. FINAL stage: WinBox light show, FS package, buy cards, loading, anticipation, purge of
   ALL template assets, paytable/rules content, sticky symbol.
10. QC rounds: symbol normalization/centering, lattice alignment, size hierarchy, landscape
    board conforming to crystal-v2 frame (CELL_W refactor), sky-realm backgrounds +
    day/night swap under transition, seamless trail hand-off, wild line completion, thin
    right-extending paylines, click-to-skip (lines + spins + anticipation), bokeh
    particles, multiplier badge pops, sticky badge placement, payline-set correction +
    independent win re-evaluation audit gate.

---

## 7. Environment notes

- Windows 11; python venv at `math/env`; pnpm at `~/AppData/Roaming/npm/pnpm.cmd`;
  storybook launch config in `~/.claude/launch.json` ("storybook", port 6010).
- Image generation via Higgsfield MCP (`generate_image`, nano_banana_pro, ~2 credits/img);
  reference-based generation using previously uploaded symbol media ids.
- Agent CANNOT screenshot the WebGPU canvas (tool wedges) — visual verification is always
  the human's browser at localhost:6010; agent verifies via vite HMR log + storybook
  index.json + montages of static assets.
