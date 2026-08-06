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
- [x] **1.6 Feature intro/outro ART PLAQUE ceremony** (operator: two code-drawn versions
      both "way too sloppy" → the studio answer is painted art, not vector borders).
      SHIPPED 2026-08-03: ornate plaque plates generated via Higgsfield nano_banana_pro
      with board1.png as the style reference (cyan/prism + gold royal variants; crown
      crest + seated gems baked into the art, blank interior for text), deterministic
      flood-fill white-backdrop cutout (no ML fringe — lesson from the clouds), assets
      `platePrism`/`plateGold` (static/assets/ui/panels/). FreeSpinIntro + FreeSpinOutro
      rebuilt on the plates: impact entrance + twin silhouette shockwaves, staggered
      text beats (wordmark drop → count/amount impact with radial glint burst →
      sub-line), slow staggered light-catch glints seated on the art's gem positions,
      gem rain + breathing backdrop bloom behind. SUPER intro = gold plate. ALSO:
      mote.png rebuilt as a true zero-edge gaussian (256px) — the old texture leaked
      alpha 12 at its quad edge, which read as a visible SQUARE around every scaled-up
      glow (the intro's "8" pool). Fixes all soft light game-wide.
      FOLLOW-UP 2 (operator): (a) outro amount was sized against a LONG test string —
      the responsive fit only shrinks, so short amounts ("$47.75") rendered huge and
      crowded the bottom inlay → base size now set for the short case (0.82S), rows
      re-centered (title -0.15H / label +0.015H / amount +0.175H); intro count nudged
      up (+0.09H → +0.065H). (b) FREE-SPIN COUNTER redesigned as a MINIATURE of the
      intro plaque (same platePrism/plateGold assets — the feature's sigil): count is
      the hero with an impact pop + crown-gem glint per spent spin, idle catch-light,
      accent pool under the numerals, gold plate under SUPER. NOTE: menu pod observed
      OPEN at boot twice during verification with zero clicks — folded into the
      flagged overlay-discipline gap.
      FOLLOW-UP 3 (operator: "something more actually designed"): tried a Flux 1.1
      Pro ornate crystal plaque (Replicate; Higgsfield plan-gated even with credits,
      Gemini quota 0, OpenAI imagegen server bug) + in-repo gold hue-derivation —
      operator: "way too over done, align with the limestone of the board outer."
      FINAL (v6 after "too realistic, not the cartoon vibe of the board"):
      counter_stone.png is DETERMINISTICALLY RENDERED (scratch gen_counter_stone.py,
      seeded) in the frame's HAND-DRAWN language — palette and outline color SAMPLED
      from board1.png itself (creams ~74%, teal/mauve/blue-gray/rose accents ~26%,
      outline near-black plum 52,14,44), bold wobbly outlines (midpoint-jitter
      edges), soft elliptical per-facet light washes, accents spread by ring angle
      (never clumped), chamfered silhouette, dark violet glass window with
      center-darkening — reads as a piece cut from the board frame. v7: ink made
      DISPLAY-CALIBRATED — the counter shows at ~0.14x art scale, so the board's
      bold black contour must be ~18px in art pixels (silhouette, near-black
      24,8,22) / 15px (window rim) / 10px (facet lines) to land at the frame's
      on-screen line weight; the earlier "correct-looking" 4px contour rendered
      sub-pixel and vanished. Single asset `counterStone` for
      both modes; SUPER identity carried by the accent light pool (gold vs cyan),
      which also FLARES briefly on each spent spin alongside the count's impact pop.
      Ornate counter assets deleted. Flux gens kept on Desktop/breakroom-assets if
      ever wanted. AI-gen lesson logged: Flux ignores in-prompt aspect directives
      and drifts ornament ("NO gold filigree" → gold filigree) — for precise UI
      chrome, deterministic rendering beats prompting.
      FOLLOW-UP (operator, same day): (a) "PRESS ANYWHERE TO CONTINUE" now seats WITH
      the box on all three ceremony surfaces (intro/outro: under the plaque; big-win
      box: under the box, and only once the roll completes and the box holds — mid-roll
      a press means "advance a tier") via PressToContinue `showLabel={false}` + a local
      invite line; the screen-bottom label read as disconnected. (b) Text rows re-seated
      against MEASURED art safe zones (crown/wing blades intrude to -0.246H cyan /
      -0.259H gold; interior bottom +0.366/+0.358): intro word -0.14H / count +0.09H /
      sub +0.305H, outro title -0.15H / label +0.03H / amount +0.20H — the wordmark had
      been colliding with the crown's wing blades.
- [~] **1.5 Near-miss decompression (subtle).** When scatter anticipation ran and the
      trigger whiffed at 2 scatters: a quiet two-note descending exhale + slightly
      softer anticipation release. No dim, no banner. Skipped when a win presentation
      follows (the win owns the stage).

- [x] **1.7 Ceremony plates unified on LIMESTONE + pulse sync + line layering**
      (operator 2026-08-04: gold plate "way too overdone, we need a more clean
      design"; amount/box pulses "alternating looks weird"; line behind symbols;
      more symbol react). (a) Intro/outro rebuilt on plate_stone.png (scratch
      gen_plate_stone.py — the counter's limestone generator at ceremony scale, ink
      recalibrated for ~0.37x display: contour 7px/rim 6px/facets 4.5px art-px);
      ornate plate_cyan/plate_gold DELETED; single stone plate both modes, SUPER =
      gold accent light only; rows re-seated symmetric (intro word -0.19H / count
      +0.055H / sub +0.28H; outro title -0.20H / label +0.005H / amount +0.19H).
      (b) PULSE SYNC: count/amount idle scales removed — they settle to exactly 1
      and inherit the plate container's breath (two sines at different frequencies
      read as ALTERNATING). (c) WIN LINES render BEHIND the symbols: first attempt
      put the ribbon under the ANIMATE-layer BoardBase — wrong, because every board
      symbol is a SPRITE (winners live in the STATIC layer; the animate layer only
      ever shows spine symbols), so the ribbon still drew over them. Fixed: WinLines
      sits inside the STATIC BoardContext, masked, between BoardMask (cell backdrop)
      and BoardBase — ribbon under ALL symbols, visible only in the cell gaps;
      badges/value pop still top everything. (e) WIN BOX v4 = STONE (operator: "this
      win box is nothing like the game board"): PrismPanel replaced with the
      plateStone sprite (6.2S wide, aspect from art); corner gems / crest / crown /
      drawGem jewellery DELETED — the full tier ladder lives in LIGHT (accent
      ladder on every bloom/pool/divider/sweep/shockwave/spark, word size per tier,
      EPIC gem rain, MAX gold storm); shockwave/sweep octagon re-cut to the stone
      chamfer (0.148H); WORD_MAX_W + amount maxWidth tightened to 4.3S to stay
      inside the stone window (half-width 2.30S). Verified live: BIG hold, staged
      roll with pins, promotion impact (word burst + flash + shockwaves) mid-frame,
      EPIC hold with gem rain. RetriggerBanner is the LAST PrismPanel user — likely
      wants the stone treatment for consistency (not yet directed).
      (d) HIT SWELL: ReelSymbol adds a +10% one-swell envelope
      (550ms, winSpeed-scaled, shared trailClock acquired only while winning) on top
      of the spine's own win reaction.

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

## STUDIO-QUALITY PHASE — A+ AUDIT MAP (2026-08-04, 9-agent sweep: 133 findings, 27H/59M/47L)
Full machine-readable findings: session task output w7laozv78. Prioritized execution:

### WS1 — Mobile/portrait UI lock (operator ref: Campfire hierarchy)
- [x] Portrait console v2: ROW1 buy | [-]bet[+] | hero | auto+turbo, ROW2 menu | balance | win;
      drawer folds rows, WIN holds ground, FS counter takes balance slot; board 0.44H portrait.
- [x] Menu-open-at-boot MYSTERY SOLVED: test-rig cursor-position focus-click, NOT a game bug.
- [ ] H: ButtonDrawer = raw template black blob + '↓' fallback glyph (rebuild UiGlass+chevron)
- [ ] H: AutoSpin counter double-offset black rect collides with hero (fix offset + crystal restyle)
- [ ] H: Buy-bonus modal portrait 0.41x scale-to-fit = illegible (vertical stack rework)
- [ ] H: Modals 50% root-font hack = 6-8px text on phones (delete + deliberate portrait scale)
- [ ] H: BaseIcon template black rects across bet/autoplay/settings/buy-confirm (crystal keys)
- [ ] M: portrait tap targets <44pt (steppers/menu); portrait type tokens ~1.8x small;
      folded drawer button half off-screen; FS balance+bet both hidden (cert risk);
      LabelBet secret button w/o affordance+press guard; no grounding shadows/prism seam;
      Popup children rendered twice; UIReplay raw template; logo REM-sized (29% of phone width)
### WS2 — Audio overhaul (operator: chime-heavy, replace nearly all)
- [ ] H: music transitions all hard cuts (add crossfade in createPlayMusic + route all swaps)
- [ ] H: spin itself silent (launch whoosh + spin bed + 5 pitched reel stops)
- [ ] H: win levels 1-5 fully mute, no count-up tick anywhere (level stings + roll tick)
- [ ] M: winlevel bed starts at FINAL tier during roll (step per promotion); no ducking
      (jingle vs bed); dragon_land triple-duty; retrigger reuses trigger sting + banner silent;
      6 bet modes share one identity; FS curtain silent; buy-confirm = generic click;
      sfx_wild_explode + sfx_winlevel_end dead cues
- [ ] Full replacement set scoped by inventory finding (28 cues + gaps); tools/sound_design.py
### WS3 — Logo (operator: current looks awful)
- [ ] Regenerate PRISM PATH wordmark in game language; also fix logo sizing (REM*7 canvas px)
      + 1.16MB PNG at 112px display
### WS4 — Small stuff / surfaces
- [ ] H: paytable/rules symbol images ALL BROKEN (symImg dynamic URL -> undefined)
- [ ] H: rules omit HUNT/DRAGON3/DRAGON5 modes; no payline diagram (17 lines); mobile
      legibility of info pages
- [ ] H: template loader chain ('Add Your Loader' 2s every boot) still ships (+layout.svelte)
- [ ] H: RGS error = permanent dead screen w/ raw JSON (reload action + human copy)
- [ ] H: boot->game reveal hard pop (crossfade handoff)
- [ ] H: 9.4MB dead bgBase/bgFeature preloads (delete); 40MB _generated_src in static/ (move out)
- [ ] H: MenuPod hard-cut open/close (tween); small-win presentation has no impact beat
- [ ] M: menu pod z-under ceremonies + never auto-closes (reset menuOpen on bet/feature start —
      ButtonMenu pressCatcher gate DONE); settings sliders native; sound toggle destroys volume
      setting; EXIT label lies; Popup chrome unstyled x; modal body text in display font;
      console press/hover snaps (tween); hero SPIN<->STOP one-frame swap; dead console idle
      (no shimmer); BoardFrame feature glow event dead; ceremony exits limp vs entrances;
      sticky marker birth pop-in; retrigger total bump no motion; FS counter/balance overlap beat;
      autoplay fires behind modals; asset-load failures silent; prismBeast.png placeholder ships;
      buy cards style-mismatch (cavern serpents) + 4.3MB PNGs; bg layers soft on hi-DPI (2x recut);
      night bank plate missing; version '0.0.0' player-visible
- [ ] L: 47 craft-debt items (dead code, duplication, i18n stubs, a11y) — see task output
### WS5 — Math shaping + 100K books
- Baseline: paytable FLAT (L* 0.25/0.5/1.0; H*+WILD 0.5/1.5/5.0), strips identical per reel
  (BR0 L2:7 L3:8 L4:9 L5:10 H1:4 H2:4 H3:3 H4:2 W:2 S:1 of 50), dragons 64% of spins,
  scatter 1/116 vs 1/200 pricing anchor, flat-LUT base mean 100x. Wincap 5000x (10,000x
  deferred to RTP pass per standing directive).
- [ ] Rank-tiered paytable + royals spread; H4 premium; per-reel strip shaping; WILD rarity cut;
      scatter to ~1/200; padding mult table per gametype; mirror frontend config.ts + paytable UI;
      probe 10K -> iterate feel -> 100K books + validator + invariants

### Studio-phase execution log (2026-08-04, session 2)
- [x] WS5 MATH: rank-tiered paytable landed (J/Q/K/A 0.15-0.25 -> 0.80-1.25 at 5-kind;
      gems purple 0.40/1.20/3.00 -> green -> blue -> red 1.25/4.00/10.00 = WILD-run tier);
      strips rebuilt per-reel on 100-row columns (dragons E0.40/board base, E0.65 free;
      scatter thinned reels 4-5 to ~1/220 natural; premium H1 thinner reels 1-2; purple
      most common gem); padding mult table split per gametype. 100K corpus generated
      (60K base/10K bonus/10K super/10K hunt/5K d3/5K d5), validator 100,000/0,
      invariants 0. Corpus feel: base mean 45.7x hit 60% med 1.20x p90 65x —
      dust+dragon-tails volatility; story books re-extracted + scenarios copied.
      REMAINING: frontend config.ts + paytable UI mirror (agented), then the deferred
      RTP/LUT optimizer pass (separate standing item, incl. 10,000x).
- [x] WS1 batch: portrait console v2 verified; ButtonDrawer rebuilt (UiGlass+chevron,
      UiSprite/UiDoublePress deleted); autospin counter fixed+crystal; menu 118std +
      folded drawer on-screen + FS compact balance (drawerFold-gated) + labelScale
      portrait type boost; MenuPod rise/fade motion; menuOpen reset on uiHide +
      pressCatcher gate; board 0.44H portrait. Boot-open pod = test-rig cursor artifact
      (verified by parking cursor; NOT a game bug).
- [x] WS3 LOGO: new bubble-crystal wordmark (Flux, cutout, TM scrubbed, 640px, 4.6/7 REM
      portrait/desktop + top inset). Old 1.16MB logo replaced.
- [x] WS4 batch 1: paytable symImg import.meta.glob fix; 'Add Your Loader' chain deleted;
      9.4MB dead bg preloads deleted; _generated_src (40MB) moved to art_src/; 50% root
      font hack -> 87.5%; ac3/DS_Store/prismBeast placeholder/beastDown dup/FRWCAP purged
      (static 77MB -> 23MB); hit-swell scaled-time fixed; SmallWinPop impact beat.
- [~] WS2 AUDIO agented (warm palette rewrite + coverage cues + crossfade + wiring).
- [~] WS4 batch 2 agented (BaseIcon crystal, buy-modal portrait stack, error modal,
      Popup chrome+dup, sliders+volume memory, rules/paylines/paytable-derive, app.html).

### 2026-08-05 — WIN BOX DIRECTION SETTLED (operator)
The stone win box (v4) is OUT: "I liked the progressive ones we had before with the
gems." WinBox v3.2 RESTORED verbatim from commit 32f757e (opaque violet PrismPanel,
tier accent ladder, corner gems SUPER+, crest + side stones + EPIC crown, all
promotion ceremonies) with the v3.2 amount sizing (4.6S width / 1.3S font) back in
Win.svelte — the amount-overlapping-the-box report was the stone window's shorter
interior (+0.72S row vs 1.15S half-window) and clears in v3.2 geometry (verified at
$31.95 SUPER WIN live). SCOPE NOTE: stone stays where approved — FreeSpinIntro/Outro
plates + free-spin counter + board frame family. The WIN BOX is the progressive
gem plaque, canon.

### 2026-08-05 — quick-spin + feel tweaks (operator batch)
- [x] Dragon glide whoosh RESTORED to the original voice (lowpass 1900 / damp 3600 —
      the warm pass had darkened it); sprite regenerated.
- [x] Board-breath launch cue trimmed to its FIRST part (whoosh only — the thump+pluck
      tail read as a second event).
- [x] Frosted grid: pre-blurred day/night sky plates (4KB each) masked under the board
      glass — scene-aware, subtle.
- [x] QUICK-SPIN: (a) value pops get a LEGIBILITY FLOOR (pop window advances max 2x
      real time — can't compress to a blip or be jumped over); (b) engaging turbo
      mid-flight SLAMS all reels together via enhancedBoard.stop() (guarded to paced
      spin types so pre-toggled turbo keeps designed timing).
- [x] Z-ORDER: BoardBase split into trail/nonTrail passes around WinLines — the line
      rides OVER dragon path cells, under all other symbols and multiplier badges.
- [x] BET UI STRUCTURAL: hero DETACHED from the deck (bar no longer runs under the
      glass — nothing shows through at spin-time dim); BET/STOP label removed, glyph
      up to 0.52D.
- [x] BET UI corrected per operator: CONNECTED structure restored (hero back on the
      deck's end cap — detaching was a misread). The polish fix is in ButtonBet:
      disabled no longer applies container transparency (which let the bar read
      through the glass); the face stays fully opaque and "dimmed" is a dark veil
      disc drawn OVER it. Label-less enlarged glyph kept.
- [x] PLATES REBUILT FROM THE REAL FRAME ART (operator: stone renders "super dull and
      just off"): tools/compose_plates.py recomposes board1.png itself into
      plate_stone.png + counter_stone.png — corners verbatim, sides as two
      corner-continuous halves with a feathered mid-seam, top/bottom bars closed with
      one feathered seam at the least-inked column, ring alpha-composited over the
      dark-glass window. Ring scaled so border thickness matches the existing
      component text-inset geometry (zero frontend changes). The plaques now inherit
      the frame's true washes/iridescence/sparkles by construction. Intro shares the
      plate asset — all three surfaces upgraded together.
- [x] PLAQUES v3 — DESIGNED, not copied (operator: "it can't just be a copy, it has
      to align"). tools/gen_plaques.py (compose_plates.py deleted) implements the
      frame's DESIGN GRAMMAR at plaque proportions: radial bezel facets inner
      window -> gem-cut outer edge (leaning spokes, irregular widths, occasional
      internal detail lines), per-facet painted washes, the frame's color script
      (creams + rare SATURATED red/teal/purple/rose facets + HOLOGRAPHIC rainbow
      facets, spread by ring position), plum ink hierarchy with hand wobble at
      display-calibrated widths, star sparkles at junctions. Ceremony plate K=24
      medium ink (~0.37x display); counter K=13 chunky facets heavy ink (~0.14x).
      Window insets unchanged -> zero component edits. Verified in-game: outro +
      counter + (shared-asset) intro.
- [x] CEREMONY DESIGN SETTLED — THE WIN-BOX FAMILY IS THE DIALOG LANGUAGE (operator
      rejected every stone/frame-derived panel: the board frame is the PLAY surface,
      not the dialog anchor; the approved dialog design is the progressive gem
      plaque). FreeSpinIntro + FreeSpinOutro now RIDE WinBox ITSELF (new
      accentOverride prop): intro = level-7 cyan plaque (SUPER = level-9 gold with
      crown + gem rain), outro = level-9 GOLD ("FREE SPINS COMPLETE" / TOTAL WIN /
      static amount with one impact beat). FreeSpinCounter = miniature of the family
      (opaque PrismPanel, accent pool + tick flare, two seated corner stones, gold
      under SUPER). Stone assets/generators DELETED (plate/counter_stone pngs,
      gen_plaques/compose tools, registry entries). Verified live on a fresh server:
      intro/outro/counter render, zero panel asset requests, no compile errors.
- [x] Counter gems dropped (operator); intro/outro pulse as ONE — WinBox wordmark's
      idle sine removed (settles to exactly 1, inherits the plaque breath — same
      rule as the ceremony amounts), which also unifies the big-win box's own
      word/box breathing. (Dev-only note: intermittent stale-module 404s for the
      deleted stone assets were the browser pane's HTTP cache — repo verified clean,
      impossible in hashed production builds.)
- [x] LOOP BLIP FIXED (operator: audible blip every couple seconds in the bonus):
      fold_loop preserved tail ENERGY across the wrap but never matched the
      WAVEFORM at the seam — noise-based beds (2.0s spin loop, running constantly
      through bonus autoplay; 0.9s dragon glide during flights) had uncorrelated
      end/start samples = a click every cycle. New seamless_loop() applies an
      equal-power circular crossfade (end blended into start, 35ms) to EVERY
      loop=True cue at build time, with a printed seam-jump check. Regenerated:
      all 12 looping cues now measure seam jumps 0.001-0.012 (vs ~0.3+ raw noise
      mismatch). Sprite rebuilt; boot + spin exercised clean.

### 2026-08-05 — AUDIO DE-CLUTTER (operator: double whoosh / thin glide / too many sounds)
- [x] DOUBLE WHOOSH root-caused: TWO cues each contained a whoosh and both fired per
      spin — sfx_btn_spin on press, then sfx_spin_launch on reveal ~a beat later.
      Fix: the PRESS cue is the spin whoosh; sfx_spin_launch RETIRED, and the reveal
      only sounds sfx_btn_spin when there was no press (autoplay / space-hold), so
      every spin has exactly one. Verified by cue-trace: manual reveal = stops only;
      autoplay reveal = 1x sfx_btn_spin.
- [x] DRAGON GLIDE rebuilt (was thin/scratchy — it was pure bandpassed NOISE sweeping
      up to ~2kHz). Now built the other way round: a warm TONAL core carries it (78Hz
      + fifth + sub octave, slow pitch drift = mass displacing air), with dark filtered
      air at 30% riding on top, capped at 900Hz/1.2kHz so the harsh band is gone;
      longer 1.6s loop = slower, less swishy motion; more reverb body.
- [x] CLUTTER CUT (3 cues retired, 45 -> 42): sfx_spin_loop (constant airy bed under
      EVERY spin — background noise with nothing to say), sfx_spin_launch (above),
      sfx_wild_explode (was layered UNDER the ignition chord = two hits on one beat).
      Plus two duplicate ANNOUNCEMENTS removed: the dragon arrival cue (the same
      dragon already chimed on its reel-land ~1s earlier — one dragon, one sound) and
      the win stings on levels 2-3 (every winning line already plays sfx_winlevel_small,
      so the sting doubled the most COMMON wins; stings kept on 4-5 where escalation
      reads as intentional). Dead spine wildExplode listener + unused import deleted.
- [x] Coverage re-verified: every broadcast name exists in the 42-cue sprite, no
      orphans, all 11 loops seamless (seam jumps <= 0.0039). Bonus round cue-traced
      end to end: dismiss -> 5 reel stops -> 1 land per dragon -> 1 glide + 1 ignition
      per flight -> line cue -> big-win bed. No background bed, no doubled beats.
- [x] QUICK-SPIN LINE VALUES RESTORED (operator: quick-spinning before the reels land
      showed only ONE total pop instead of the individual line values). Root cause: the
      winInfo handler BRANCHED under turbo into a separate composite path
      (winLinesFlash) that drew bare strands with no per-line value and ended on a
      single combined total. Fix: that branch is DELETED — turbo now runs the SAME
      per-line tour as normal play with the clock pre-raised (winSpeed 5), so every
      line still pops what it paid, just at quick-spin pace (the value-pop legibility
      floor keeps each number readable at 5x). Dead flash path removed entirely
      (winLinesFlash event type, subscription, playFlash, strandOnce). Verified live:
      a turbo round produced 6 distinct value pops incl. a multiplied line rolling
      $10.00 -> $20.00, and a 5x freeze-frame shows the value + x3 badge legible
      mid-merge.
