# PRISM PATH — Studio Polish Roadmap

Living tracker for the phase-by-phase polish program. Phases activate **only on operator
direction** — items below a phase heading are not started until the operator scopes them.
Status: `[ ]` proposed · `[~]` in progress · `[x]` shipped · `[-]` dropped by operator.

## Standing design directives (operator)

- **MAX WIN becomes 10,000×** (2026-08-03). Do NOT rework the math yet — this lands with
  the RTP-convergence math pass. Until then the shipped math caps at 5,000× and every
  player-facing surface (rules note, intro card, max-win presentation) must keep saying
  5,000× so the UI never claims more than the math pays. When the math pass runs:
  wincap 500000→1000000, win-level bands, LUTs, intro card art/copy, rules copy.
- Tier-up moments, retrigger, near-miss etc. must be **tasteful** — escalation through
  light/composition, not clutter. Near-miss specifically **subtle**.
- Operator playtests in their own browser; nothing is committed until they say so.

---

## Phase 1 — WIN EXPERIENCE  `ACTIVE`

- [~] **1.1 Win box redesign (foundation).** Rebuild the box as a designed composition
      before layering tier-ups onto it: tier crest gem seated on the plaque's top edge,
      refined divider (end-cut diamonds), radial under-glow behind the amount, tier accent
      running through every light. Same cut-crystal plaque base.
- [~] **1.2 Tier-up moments.** The box ranks up LIVE as the count-up crosses tier bands
      (BIG 15× → SUPER 30× → MEGA 50× → EPIC 100× → MAX at cap): wordmark re-drop with
      impact, accent morph, crest re-cut pulse, expanding flash ring, rank-up stinger.
      Display tier is clamped to the book's final level — presentation never oversells.
- [~] **1.3 MAX WIN presentation.** Now: a distinctly heavier gold-storm treatment for the
      MAX tier inside the new box system (gold veil, denser rays, gold crest). The full
      bespoke scene (dragons, screen-wide sequence) lands WITH the 10,000× math pass so
      it's built once against the real cap.
- [~] **1.4 Retrigger banner.** "+N FREE SPINS" crystal plaque beat inside the retrigger
      presentation — pop-in impact, short hold, out. Tasteful, no screen takeover.
- [~] **1.5 Near-miss decompression (subtle).** When scatter anticipation ran and the
      trigger whiffed at 2 scatters: a quiet two-note descending exhale + slightly
      softer anticipation release. No dim, no banner. Skipped when a win presentation
      follows (the win owns the stage).

## Phase 2 — GAME FEEL / CHOREOGRAPHY  `ACTIVE`

- [x] **2.1 Designed turbo win presentation** (operator: skipping anticipation IS the
      point of turbo — keep; win lines must not read as "10x footage"). SHIPPED: under
      turbo (incl. space-hold), winInfo presents ONE composed statement — all lines
      sweep on in a 45ms-stagger cascade with full easing, all winning symbols breathe
      together, the combined total pops once at the collective centroid, joint release.
      ~0.7s flat. Normal-speed play keeps the line-by-line tour; click-skip unchanged.
- [-] 2.2 Dragon charge inhale — DROPPED by operator: the current smooth launch is better.
- [~] **2.3 LIVING BACKGROUND v3 — LAYERED PLATES (operator-directed architecture,
      2026-08-03).** v1 overlays and v2 displacement both rejected; v3 is the real
      thing: the paintings DECOMPOSED into independent plates via Higgsfield
      (nano-banana image-to-image on the original art) — an empty-sky base per scene
      (day sky + aurora night sky), every island redrawn COMPLETE (including
      canvas-cropped parts, so floating never reveals a cut edge) and cut out via
      background removal, plus cloud plates. Composited in BackgroundScene.svelte in
      the painting's own 2048x1143 space: islands FLOAT (desynchronized bob + sway,
      far = less motion), clouds DRIFT. Day scene verified live (motion proven by
      inter-frame diff, composition matches the original). Night scene wired with the
      same rig — placement needs the operator's playtest eye. Old flat bg sprites kept
      as assets for instant rollback.
- [x] **2.4 Camera focus on wins** — SHIPPED with restraint: 1.4% board micro-shrink
      behind the dim veil (stateFx.boardFocus, easeInOut 320ms) while any big-win box
      or the outro panel holds; releases on hide. All BoardContainer layers move as one.

## Phase 3 — AUDIO SYSTEMS

- [ ] 3.1 Adaptive music: stems duck under win cues (envelope, not cuts); anticipation adds a tension layer instead of a second loop.
- [ ] 3.2 Quantized stingers on feature transitions (bar-aligned).
- [ ] 3.3 Spatial pan: reel stops L→R across reels; dragon glide pans along travel.
- [ ] 3.4 Bus-level mix pass (music vs SFX loudness targets).

## Phase 4 — VISUAL / ART

- [ ] 4.1 Restyle buy-confirm dialog + settings/paytable modal shells to the crystal language (last template-styled surfaces).
- [ ] 4.2 Multiplier chips on small cut-crystal backing plates.
- [ ] 4.3 Background parallax (2–3 drifting layers / slow cloud drift).
- [ ] 4.4 Logo refinement pass.
- [ ] 4.5 Night-tinted frame variant for the feature.

## Phase 5 — PERFORMANCE

- [ ] 5.1 Shards → single ParticleContainer with plain arrays (drop per-particle Svelte reactivity).
- [ ] 5.2 Asset budget: spritesheet/atlas symbols, WebP pass, resize card art to display size.
- [ ] 5.3 Redraw audit: cache static Graphics layers, bound additive overdraw.

## Phase 6 — MOBILE / RESPONSIVE

- [ ] 6.1 Designed portrait pass (board scale, thumb-zone console, buy placement).
- [ ] 6.2 Fix: free-spin counter vanishes on desktop→portrait mid-feature.
- [ ] 6.3 Touch affordances: pressed states, min hit sizes, safe areas, mid-spin orientation change.
- [ ] 6.4 In-game prefers-reduced-motion support (shards, parallax, shimmers degrade).

## Phase 7 — TRUST / CERT SURFACE

- [ ] 7.1 Real version stamp (currently 0.0.0).
- [ ] 7.2 Payline diagram graphic (17 lines) in rules.
- [ ] 7.3 i18n routing for hardcoded strings.
- [ ] 7.4 RGS retry/backoff + styled error modal.

## Non-polish gate (tracked, out of scope here)

- **RTP convergence** — flat LUTs, optimizer covers 2/6 modes, must absorb 17-line +
  pay-rule uplift **and the 10,000× wincap directive above**. Single item blocking live.

## Open judgment calls (awaiting operator ruling)

- Anticipation seeding on slam paths (turbo path-dependence — folded into 2.1).
- Space-hold repainting the turbo toggle ring.
- Dead code sweep: unreachable wild-explode cue, missing 'anticipation' spine asset key, unused sfx_winlevel_end.
- **Dragon path over a scatter**: a path crossing a landed SCAT converts the cell to a
  wild for LINE pay, but the scatter still counts toward the trigger (counted at
  landing — enforced by invariants T1/T3, industry standard, player-favourable). The
  cosmetic edge: the trigger celebration animates a cell that now shows a wild
  (example: base book 48, spin 1). Keep the math; optionally later: keep the SCAT art
  visible under the path chip so the celebration reads true.

## Logic-sweep log

- **2026-08-03 full sweep** (operator-triggered after the reel-4 left-dragon sighting):
  40 agents, 16 deduped findings, 13 confirmed after 2-lens adversarial verification,
  all fixed same day. Root cause of the sighting: paytable inversion made "highest win
  per line" truncate completed lines through royals (7,353 corpus occurrences) →
  replaced with the LINE-EXTENSION RULE in engine + validator. Other majors: sticky
  claim-upgrade clobbered crossing multipliers (chip vs paid mult), space-hold rebet
  loop dead in the normal gesture (canArm raced its own keypress), resume machine
  missing onError (frozen session on handler throw), wincap-suppressed retrigger
  tripping gate T2. Minors: RTP tally double-clamp on capped rounds, counter staleness
  across features + no rehydrate on remount, resume celebration on placeholder board,
  float micro-unit wire amounts, space-hold arming behind modals nesting into
  autoplay, bet-machine error path skipping settlement, prismPath event docstring
  contradicting emission.
