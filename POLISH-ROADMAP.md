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

## Phase 2 — GAME FEEL / CHOREOGRAPHY

- [ ] 2.1 Turbo as a designed timing table (fix manual-turbo vs turbo-autoplay anticipation inconsistency).
- [ ] 2.2 Dragon charge inhale (~200ms pull-in before launch: seat glow swell, sparkles drawn inward).
- [ ] 2.3 Idle life: slow shimmer pass over symbols every ~8s, sticky-dragon eye flare.
- [ ] 2.4 Camera focus on wins: dim + micro-shrink board behind the win box.

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
