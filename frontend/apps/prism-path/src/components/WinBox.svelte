<script lang="ts">
	// WIN BOX v3.2 — promotion transitions dialed up (operator direction).
	//
	// TIER TRANSITION ("shatter & recrystallize", ~0.75s, mostly overlapped):
	//   ANTICIPATE (140ms)  — the box inhales: subtle squeeze + light dims, OLD tier
	//                         still showing (the impact needs a wind-up to read clean)
	//   IMPACT (commit)     — plaque flash, board slam, stinger; the OLD wordmark
	//                         BURSTS outward (scale-up + fade) as the new one slams in;
	//                         silhouette shockwaves + star-spark burst fly
	//   RECRYSTALLIZE       — a diagonal light band SWEEPS across the plaque face and
	//                         carries the recolor: every accent LERPS old->new under it
	//   SETTLE              — overshoot breath back to rest
	//
	// The box as a whole carries a very subtle breathing pulse (replaces the orbiting
	// comets, which read as noise); corner gems sit at steady light.
	//
	// Every soft light element is now a TEXTURED gaussian sprite (the game's own `mote`
	// bokeh orb / `moteStar` glint), not a flat-filled circle: real radial falloff on the
	// blooms, comet heads with soft trails, star-sprite gem rain and promotion sparks.
	// Graphics remains ONLY for hard-edged draws that deserve it: the divider facets,
	// the corner/crest gems, and the promotion's plaque flash + silhouette shockwaves
	// (octagon strokes). The backdrop is pure soft light: a layered bloom plus three
	// huge drifting orbs (no ray pinwheel — it striped).
	//
	// Structure unchanged from v3: opaque plaque, additive tier systems
	// (BIG baseline / SUPER corner gems / MEGA comets / EPIC gem rain + crown / MAX gold
	// storm), staged-roll promotions with the layered impact stack.
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Container, Graphics, Sprite } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';

	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { getContext } from '../game/context';
	import { winLevelMap, type WinLevel } from '../game/winLevelMap';
	import { boardSlam, isUserAdvance } from '../game/stateFx.svelte';
	import { EASE, clamp01, lerpColor } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';

	type Props = {
		level: number; // FINAL tier from the book, 6..10 (big..max)
		amount?: number; // current rolling amount (book units) — enables live tier-up
		fixedText?: string; // outro-style callers: wordmark stays put
		accentOverride?: number; // feature ceremonies borrow the plaque with their own accent
		children: Snippet;
	};
	const props: Props = $props();
	const context = getContext();

	// ---- win-level bands (book units; mirrors math get_win_level) ----
	const tierFromAmount = (a: number) => (a >= 500000 ? 10 : a >= 10000 ? 9 : a >= 5000 ? 8 : a >= 3000 ? 7 : 6);
	const displayLevel = $derived(
		props.amount === undefined
			? Math.max(6, Math.min(10, props.level))
			: Math.max(6, Math.min(props.level, tierFromAmount(props.amount))),
	);
	// SHOWN tier is decoupled from the raw level: a promotion first plays a short
	// ANTICIPATION beat on the old tier, then commits on the impact frame
	let shown = $state(0); // 0 = uninitialised; else 6..10
	let pendingSince = -1e9; // when the raw level rose past `shown`
	let prevWord = $state('');
	let prevAccentColor = $state(0);

	const GOLD = 0xffd25e;
	const ACCENTS = [0x2bb8e8, 0x34c0a1, 0x9b3ce8, 0xff5db1, GOLD] as const;

	const shownLevelSafe = $derived(shown === 0 ? Math.max(6, Math.min(10, displayLevel)) : shown);
	const word = $derived(props.fixedText ?? winLevelMap[shownLevelSafe as WinLevel].text ?? '');
	const tier = $derived(shownLevelSafe - 6); // 0..4
	const WORD_SIZE = $derived(SYMBOL_SIZE * (1.1 + tier * 0.1));
	const isMax = $derived(shownLevelSafe >= 10);
	const accentTarget = $derived(props.accentOverride ?? ACCENTS[tier]);

	const BOX_W = SYMBOL_SIZE * 6.2;
	const BOX_H = SYMBOL_SIZE * 3.6;
	const CUT = Math.min(26, Math.min(BOX_W, BOX_H) * 0.16);
	const WORD_MAX_W = BOX_W - SYMBOL_SIZE * 0.9;
	const WORD_Y = -SYMBOL_SIZE * 0.78;
	const DIVIDER_Y = -SYMBOL_SIZE * 0.02;
	const AMOUNT_Y = SYMBOL_SIZE * 0.78;
	const CREST_Y = -BOX_H / 2;

	const octagon = (w: number, h: number): number[] => {
		const w2 = w / 2;
		const h2 = h / 2;
		const c = CUT;
		return [-w2 + c, -h2, w2 - c, -h2, w2, -h2 + c, w2, h2 - c, w2 - c, h2, -w2 + c, h2, -w2, h2 - c, -w2, -h2 + c];
	};
	const scaleOct = (pts: number[], s: number) => pts.map((v) => v * s);

	const jitter = (i: number, salt: number) => {
		const v = Math.sin(i * 127.1 + salt * 311.7) * 43758.5453;
		return v - Math.floor(v);
	};

	let nowMs = $state(0);
	let born = 0;
	let introStartMs = $state(0);
	let rankAtMs = $state(-1e9);

	onMount(() => {
		born = performance.now();
		nowMs = born;
		introStartMs = born;
		let raf = 0;
		const frame = () => {
			nowMs = performance.now();
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	const ANTICIPATE_MS = 140;

	const commitPromotion = (to: number) => {
		prevWord = props.fixedText ?? winLevelMap[Math.max(6, shown) as WinLevel].text ?? '';
		prevAccentColor = ACCENTS[Math.max(0, shown - 6)];
		shown = to;
		pendingSince = -1e9;
		introStartMs = performance.now();
		rankAtMs = performance.now();
		boardSlam(0.45);
		context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_tier_up' });
	};

	$effect(() => {
		const raw = displayLevel;
		if (shown === 0) {
			shown = raw; // first paint: no ceremony
			return;
		}
		if (raw > shown && pendingSince < -1e8) {
			if (isUserAdvance()) {
				commitPromotion(raw); // a press drove this — respond on THIS frame
			} else {
				pendingSince = performance.now(); // organic roll: start the inhale
			}
		} else if (raw < shown) {
			shown = raw;
			pendingSince = -1e9;
		}
	});

	// the shared rAF clock also drives the anticipate->commit handoff
	$effect(() => {
		void nowMs;
		if (pendingSince > -1e8 && performance.now() - pendingSince >= ANTICIPATE_MS) {
			if (displayLevel > shown) commitPromotion(displayLevel);
			else pendingSince = -1e9;
		}
	});

	const pendAge = $derived(pendingSince > -1e8 ? (nowMs - pendingSince) / 1000 : 1e9);

	const t = $derived((nowMs - born) / 1000);
	const intro = $derived(clamp01((nowMs - introStartMs) / 420));
	const rankAge = $derived((nowMs - rankAtMs) / 1000);

	// after the drop-in impact the wordmark settles to EXACTLY 1 and breathes WITH
	// the plaque (operator: its own idle sine at another frequency read as the word
	// and the box pulsating independently — same rule as the ceremony amounts)
	const wordScale = $derived.by(() => {
		if (intro < 1) return 1.9 - 0.9 * EASE.impact(intro);
		return 1;
	});
	const wordAlpha = $derived(clamp01(intro * 2.2));

	// RECRYSTALLIZE: every accent lerps old->new while the light band sweeps the plaque
	const easeIO = (u: number) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2);
	const accent = $derived.by(() => {
		const u = clamp01(rankAge / 0.32);
		return u < 1 && prevAccentColor ? lerpColor(prevAccentColor, accentTarget, easeIO(u)) : accentTarget;
	});
	const sweepU = $derived(clamp01(rankAge / 0.38));
	// old wordmark bursts outward on the impact frame
	const prevBurstU = $derived(clamp01(rankAge / 0.24));

	const boxScale = $derived.by(() => {
		const u = clamp01(t / 0.36);
		let sc = 0.86 + 0.14 * EASE.impact(u);
		// ANTICIPATE: the inhale squeeze before the impact commits
		if (pendAge < 0.2) sc *= 1 - 0.035 * Math.sin(Math.PI * clamp01(pendAge / 0.2));
		// IMPACT overshoot: a quick swell right after the commit, then settle
		if (rankAge < 0.5) sc *= 1 + 0.045 * Math.sin(Math.PI * clamp01(rankAge / 0.5)) * (1 - rankAge / 0.5);
		// whole-box breathing (replaces the orbiting comets): very subtle, deeper by tier
		sc *= 1 + (0.006 + tier * 0.0015) * Math.sin((t * Math.PI * 2) / 2.2);
		return sc;
	});
	// the inhale also dims the light for a beat
	const anticipationDim = $derived(pendAge < 0.2 ? 1 - 0.25 * Math.sin(Math.PI * clamp01(pendAge / 0.2)) : 1);
	const crestPulse = $derived(1 + 0.32 * Math.sin(Math.PI * clamp01(rankAge / 0.42)));
	const raysSurge = $derived((1 + 2.2 * (1 - clamp01(rankAge / 0.6))) * anticipationDim);
	const bloomIn = $derived(EASE.settle(clamp01(t / 0.55)));
	const DRIFTS = [0, 1, 2];

	// ---- gem rain (EPIC+): falling star sprites behind the plaque ----
	const RAIN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
	const RAIN_H = BOX_H * 2.1;
	const rainPos = (k: number) => {
		const u = (t * (0.16 + 0.1 * jitter(k, 5)) + jitter(k, 3)) % 1;
		return {
			x: (jitter(k, 7) - 0.5) * BOX_W * 1.55,
			y: -RAIN_H / 2 + u * RAIN_H,
			fade: Math.sin(Math.PI * u),
			size: 14 + 14 * jitter(k, 9),
		};
	};

	// ---- MAX embers: soft gold motes orbiting wide ----
	const EMBERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13];
	const emberPos = (k: number) => {
		const ang = t * (0.25 + (k % 3) * 0.08) + k * ((Math.PI * 2) / 14);
		const rr = SYMBOL_SIZE * (3.1 + 0.7 * Math.sin(t * 0.9 + k * 2.3)) * bloomIn;
		const tw = (Math.sin(t * Math.PI * 2.2 + k * 1.7) + 1) / 2;
		return { x: Math.cos(ang) * rr, y: Math.sin(ang) * rr * 0.72, tw };
	};

	// ---- promotion sparks: star sprites thrown outward on the impact frame ----
	const SPARKS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13];
	const sparkU = $derived(clamp01(rankAge / 0.55));
	const sparkPos = (i: number) => {
		const ang = (i / 14) * Math.PI * 2 + jitter(i, 11) * 0.5;
		const d = EASE.settle(sparkU) * SYMBOL_SIZE * 2.7 * (0.75 + 0.5 * jitter(i, 13));
		return {
			x: Math.cos(ang) * d * 1.15,
			y: Math.sin(ang) * d * 0.85,
			size: (1 - sparkU) * (26 + 26 * jitter(i, 17)) + 8,
			rot: jitter(i, 19) * Math.PI,
		};
	};

	const drawGem = (
		g: { poly(p: number[]): { fill(s: object): unknown; stroke(s: object): unknown } },
		x: number,
		y: number,
		G: number,
		col: number,
		alpha = 1,
	) => {
		g.poly([x - 0.42 * G, y - 0.5 * G, x + 0.42 * G, y - 0.5 * G, x + 0.72 * G, y - 0.08 * G, x - 0.72 * G, y - 0.08 * G]).fill({
			color: lerpColor(col, 0xffffff, 0.3),
			alpha,
		});
		g.poly([x - 0.72 * G, y - 0.08 * G, x + 0.72 * G, y - 0.08 * G, x, y + 0.62 * G]).fill({
			color: lerpColor(col, 0x140b24, 0.25),
			alpha,
		});
	};
</script>

<!-- ===== BACKGROUND LIGHT (behind the plaque) ===== -->

<!-- central bloom: real gaussian falloff (mote texture), accent + white core -->
<Sprite
	key="mote"
	anchor={0.5}
	blendMode="add"
	tint={isMax ? GOLD : lerpColor(accent, 0xffffff, 0.2)}
	width={SYMBOL_SIZE * (7.5 + tier * 0.7) * bloomIn}
	height={SYMBOL_SIZE * (6 + tier * 0.6) * bloomIn}
	alpha={(0.34 + 0.08 * Math.sin(t * Math.PI * 1.2)) * Math.min(raysSurge, 1.7)}
/>
<Sprite
	key="mote"
	anchor={0.5}
	blendMode="add"
	tint={0xffffff}
	width={SYMBOL_SIZE * 3.6 * bloomIn}
	height={SYMBOL_SIZE * 3 * bloomIn}
	alpha={0.22 * Math.min(raysSurge, 1.5)}
/>

<!-- drifting light masses: three huge soft orbs orbiting almost imperceptibly — the
     backdrop light BREATHES and wanders instead of striping (no ray pinwheel) -->
{#each DRIFTS as d (d)}
	{@const ang = t * (0.05 + d * 0.018) * Math.PI * 2 + d * 2.1}
	<Sprite
		key="mote"
		anchor={0.5}
		blendMode="add"
		tint={lerpColor(accent, 0xffffff, 0.15)}
		x={Math.cos(ang) * SYMBOL_SIZE * 1.35}
		y={Math.sin(ang) * SYMBOL_SIZE * 1.0}
		width={SYMBOL_SIZE * (4.6 + tier * 0.3) * bloomIn}
		height={SYMBOL_SIZE * (3.7 + tier * 0.25) * bloomIn}
		alpha={(0.11 + 0.02 * tier + 0.03 * Math.sin(t * Math.PI * 0.7 + d * 2)) * Math.min(raysSurge, 1.5)}
	/>
{/each}

<!-- MAX: breathing gold vignette (one huge soft orb, never a drawn ring) -->
{#if isMax}
	<Sprite
		key="mote"
		anchor={0.5}
		blendMode="add"
		tint={GOLD}
		width={SYMBOL_SIZE * 16}
		height={SYMBOL_SIZE * 12}
		alpha={0.1 + 0.04 * Math.sin(t * Math.PI * 0.8)}
	/>
{/if}


<!-- EPIC+: gem rain — soft star sprites drifting down behind the plate -->
{#if tier >= 3}
	{#each RAIN as k (k)}
		{@const p = rainPos(k)}
		<Sprite
			key="moteStar"
			anchor={0.5}
			blendMode="add"
			tint={lerpColor(accent, 0xffffff, 0.5)}
			x={p.x}
			y={p.y}
			width={p.size}
			height={p.size}
			rotation={jitter(k, 21) * Math.PI}
			alpha={0.75 * p.fade}
		/>
	{/each}
{/if}

<!-- MAX: gold storm embers (soft motes, not dots) -->
{#if isMax}
	{#each EMBERS as k (k)}
		{@const p = emberPos(k)}
		<Sprite
			key="mote"
			anchor={0.5}
			blendMode="add"
			tint={GOLD}
			x={p.x}
			y={p.y}
			width={10 + 14 * p.tw}
			height={10 + 14 * p.tw}
			alpha={(0.25 + 0.4 * p.tw) * bloomIn}
		/>
	{/each}
{/if}

<Container scale={boxScale}>
	<PrismPanel width={BOX_W} height={BOX_H} {accent} opaque>
		<!-- amount under-glow + wordmark bloom: soft textured pools of tier light -->
		<Sprite
			key="mote"
			anchor={0.5}
			blendMode="add"
			tint={lerpColor(accent, 0xffffff, 0.3)}
			y={AMOUNT_Y}
			width={SYMBOL_SIZE * 3.8}
			height={SYMBOL_SIZE * 2.3}
			alpha={0.3 + 0.07 * Math.sin(t * Math.PI * 1.1)}
		/>
		<Sprite
			key="mote"
			anchor={0.5}
			blendMode="add"
			tint={lerpColor(accent, 0xffffff, 0.25)}
			y={WORD_Y}
			width={WORD_MAX_W * 1.25}
			height={SYMBOL_SIZE * 1.7}
			alpha={0.26 + 0.06 * Math.sin(t * Math.PI * 1.3)}
		/>

		<!-- wordmark: auto-fit, impact drop-in (re-drops on every promotion) -->
		<Container y={WORD_Y} scale={wordScale} alpha={wordAlpha}>
			<ResponsiveBitmapText
				anchor={0.5}
				maxWidth={WORD_MAX_W}
				text={word}
				style={prismStyle(WORD_SIZE, { align: 'center' })}
			/>
		</Container>

		<!-- the OLD wordmark bursts outward on the impact frame (departing, over the new) -->
		{#if prevBurstU < 1 && prevWord}
			<Container y={WORD_Y} scale={1 + 1.15 * EASE.settle(prevBurstU)} alpha={1 - prevBurstU}>
				<ResponsiveBitmapText
					anchor={0.5}
					maxWidth={WORD_MAX_W}
					text={prevWord}
					style={prismStyle(WORD_SIZE, { align: 'center' })}
				/>
			</Container>
		{/if}

		<!-- divider: accent facet line, centre diamond + end-cut diamonds -->
		<Graphics
			blendMode="add"
			draw={(g) => {
				const half = BOX_W * 0.32;
				const breathe = 0.7 + 0.3 * Math.sin(t * Math.PI * 1.4);
				g.moveTo(-half, DIVIDER_Y).lineTo(half, DIVIDER_Y);
				g.stroke({ width: 2.4, color: accent, alpha: 0.55 * breathe, cap: 'round' });
				g.moveTo(-half, DIVIDER_Y).lineTo(half, DIVIDER_Y);
				g.stroke({ width: 0.9, color: 0xffffff, alpha: 0.5 * breathe, cap: 'round' });
				const r = 5 + 1.4 * breathe;
				g.poly([0, DIVIDER_Y - r, r, DIVIDER_Y, 0, DIVIDER_Y + r, -r, DIVIDER_Y]).fill({ color: 0xffffff, alpha: 0.75 });
				const re = 3 + 0.8 * breathe;
				for (const sx of [-1, 1]) {
					g.poly([sx * half, DIVIDER_Y - re, sx * half + re, DIVIDER_Y, sx * half, DIVIDER_Y + re, sx * half - re, DIVIDER_Y]).fill({
						color: lerpColor(accent, 0xffffff, 0.55),
						alpha: 0.7,
					});
				}
			}}
		/>

		<!-- count-up (parent-provided) in the lower chamber -->
		<Container y={AMOUNT_Y}>
			{@render props.children()}
		</Container>

		<!-- RECRYSTALLIZE sweep: a diagonal light band crosses the plaque face while the
		     accents lerp — the colour change rides the light instead of snapping -->
		{#if sweepU < 1 && prevAccentColor}
			<Container>
				<Graphics
					isMask
					draw={(g) => {
						g.poly(octagon(BOX_W, BOX_H)).fill({ color: 0xffffff });
					}}
				/>
				<Graphics
					blendMode="add"
					rotation={-0.35}
					x={(-0.95 + 1.9 * easeIO(sweepU)) * BOX_W * 0.72}
					draw={(g) => {
						g.rect(-52, -BOX_H * 1.3, 104, BOX_H * 2.6).fill({ color: 0xffffff, alpha: 0.16 });
						g.rect(-18, -BOX_H * 1.3, 36, BOX_H * 2.6).fill({ color: 0xffffff, alpha: 0.3 });
					}}
				/>
			</Container>
		{/if}

		<!-- SUPER+: corner gems seated on the plaque's own chamfers -->
		{#if tier >= 1}
			<Graphics
				draw={(g) => {
					const G = SYMBOL_SIZE * 0.26;
					const inX = BOX_W / 2 - CUT * 0.9;
					const inY = BOX_H / 2 - CUT * 0.9;
					const spots = [
						[-inX, -inY],
						[inX, -inY],
						[inX, inY],
						[-inX, inY],
					];
					for (let i = 0; i < 4; i++) {
						drawGem(g, spots[i][0], spots[i][1], G, accent, 0.92);
					}
				}}
			/>
		{/if}

		<!-- TIER CREST — faceted gem on the top edge; SUPER+ side stones, EPIC+ crown -->
		<Container y={CREST_Y} scale={crestPulse}>
			<Sprite
				key="mote"
				anchor={0.5}
				blendMode="add"
				tint={lerpColor(accent, 0xffffff, 0.4)}
				width={SYMBOL_SIZE * (1.6 + tier * 0.14)}
				height={SYMBOL_SIZE * (1.3 + tier * 0.12)}
				alpha={0.4}
			/>
			<Graphics
				draw={(g) => {
					const G = SYMBOL_SIZE * (0.52 + tier * 0.045);
					if (tier >= 1) {
						drawGem(g, -G * 1.15, G * 0.08, G * 0.5, accent);
						drawGem(g, G * 1.15, G * 0.08, G * 0.5, accent);
					}
					if (tier >= 3) {
						drawGem(g, -G * 1.95, G * 0.22, G * 0.36, accent);
						drawGem(g, G * 1.95, G * 0.22, G * 0.36, accent);
					}
					const crown = [-0.42 * G, -0.5 * G, 0.42 * G, -0.5 * G, 0.72 * G, -0.08 * G, -0.72 * G, -0.08 * G];
					const pavilion = [-0.72 * G, -0.08 * G, 0.72 * G, -0.08 * G, 0, 0.62 * G];
					g.poly(pavilion).fill({ color: lerpColor(accent, 0x140b24, 0.3) });
					g.poly(crown).fill({ color: lerpColor(accent, 0xffffff, 0.18) });
					g.poly([-0.26 * G, -0.5 * G, 0.26 * G, -0.5 * G, 0.4 * G, -0.08 * G, -0.4 * G, -0.08 * G]).fill({
						color: lerpColor(accent, 0xffffff, 0.45),
					});
					g.poly([-0.3 * G, -0.08 * G, 0.3 * G, -0.08 * G, 0, 0.48 * G]).fill({
						color: lerpColor(accent, 0xffffff, 0.12),
						alpha: 0.9,
					});
					g.poly([-0.42 * G, -0.5 * G, 0.42 * G, -0.5 * G, 0.72 * G, -0.08 * G, 0, 0.62 * G, -0.72 * G, -0.08 * G]).stroke({
						width: 1.4,
						color: 0xffffff,
						alpha: 0.55,
						join: 'miter',
					});
					g.moveTo(-0.3 * G, -0.42 * G).lineTo(0.05 * G, -0.42 * G).stroke({ width: 1.6, color: 0xffffff, alpha: 0.8, cap: 'round' });
				}}
			/>
		</Container>
	</PrismPanel>
</Container>

<!-- ===== FOREGROUND LIGHT ===== -->

<!-- PROMOTION IMPACT: plaque flash + silhouette shockwaves (hard light, Graphics) -->
{#if rankAge < 0.7}
	<Graphics
		blendMode="add"
		draw={(g) => {
			const base = octagon(BOX_W, BOX_H);
			const fu = clamp01(rankAge / 0.16);
			if (fu < 1) {
				g.poly(base).fill({ color: 0xffffff, alpha: 0.5 * (1 - fu) });
			}
			const s1 = clamp01(rankAge / 0.5);
			g.poly(scaleOct(base, 1 + 1.1 * EASE.settle(s1))).stroke({
				width: 3 + 11 * (1 - s1),
				color: lerpColor(0xffffff, accent, s1),
				alpha: 0.55 * (1 - s1),
				join: 'miter',
			});
			const s2 = clamp01((rankAge - 0.09) / 0.55);
			if (rankAge > 0.09) {
				g.poly(scaleOct(base, 1 + 0.75 * EASE.settle(s2))).stroke({
					width: 2 + 6 * (1 - s2),
					color: accent,
					alpha: 0.4 * (1 - s2),
					join: 'miter',
				});
			}
		}}
	/>
	<!-- radial spark burst: soft star sprites, not vector crosses -->
	{#each SPARKS as i (i)}
		{@const p = sparkPos(i)}
		<Sprite
			key="moteStar"
			anchor={0.5}
			blendMode="add"
			tint={lerpColor(accent, 0xffffff, 0.55)}
			x={p.x}
			y={p.y}
			width={p.size}
			height={p.size}
			rotation={p.rot}
			alpha={0.95 * (1 - sparkU)}
		/>
	{/each}
{/if}
