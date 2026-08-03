<script lang="ts">
	// FORMATTED win box — one cut-crystal plaque CONTAINS the whole statement: tier crest
	// gem seated on the top edge, wordmark (auto-fit, never screen-wide), faceted divider,
	// count-up amount over a soft under-glow. The gem-shard burst renders BEHIND this box
	// (consumers order it under) — text is always clean on top.
	//
	// LIVE TIER-UP: when `amount` (the rolling count-up, book units = bet-multiple x100) is
	// provided, the box PROMOTES ITSELF as the roll crosses the win-level bands
	// (BIG 15x -> SUPER 30x -> MEGA 50x -> EPIC 100x -> MAX at cap): the wordmark re-drops
	// with impact, the accent morphs, the crest re-cuts, a flash ring expands, a rank-up
	// stinger fires. Display tier is CLAMPED to the book's final `level` — the presentation
	// can never oversell the outcome. Without `amount` the box just shows `level`.
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';

	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { getContext } from '../game/context';
	import { winLevelMap, type WinLevel } from '../game/winLevelMap';
	import { EASE, clamp01, paletteAt, lerpColor } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';

	type Props = {
		level: number; // FINAL tier from the book, 6..10 (big..max)
		amount?: number; // current rolling amount (book units) — enables live tier-up
		fixedText?: string; // outro: wordmark stays put (accents/crest still rank up)
		children: Snippet;
	};
	const props: Props = $props();
	const context = getContext();

	// ---- win-level bands in book amount units (x100 of the bet multiple) ----
	// MUST mirror math get_win_level: big 15x / super 30x / mega 50x / epic 100x / max cap.
	const tierFromAmount = (a: number) => (a >= 500000 ? 10 : a >= 10000 ? 9 : a >= 5000 ? 8 : a >= 3000 ? 7 : 6);
	const displayLevel = $derived(
		props.amount === undefined
			? Math.max(6, Math.min(10, props.level))
			: Math.max(6, Math.min(props.level, tierFromAmount(props.amount))),
	);
	const word = $derived(props.fixedText ?? winLevelMap[displayLevel as WinLevel].text ?? '');

	// ---- tier ladder (additive escalation) ----
	const tier = $derived(displayLevel - 6); // 0..4
	const RAYS = $derived(8 + tier * 2);
	const WORD_SIZE = $derived(SYMBOL_SIZE * (1.1 + tier * 0.1));
	const GOLD = 0xffd25e;
	const isMax = $derived(displayLevel >= 10);
	// tier accent ascends the game's own spectrum: cyan -> teal -> violet -> pink -> GOLD.
	// Every light in the box (rays, crest, shimmer, divider, glow) takes the accent, so
	// each tier reads as one colour statement instead of a random rainbow.
	const ACCENTS = [0x2bb8e8, 0x34c0a1, 0x9b3ce8, 0xff5db1, GOLD] as const;
	const accent = $derived(ACCENTS[tier]);

	// the box: everything lives inside this footprint
	const BOX_W = SYMBOL_SIZE * 6.2;
	const BOX_H = SYMBOL_SIZE * 3.6;
	const WORD_MAX_W = BOX_W - SYMBOL_SIZE * 0.9;
	const WORD_Y = -SYMBOL_SIZE * 0.78;
	const DIVIDER_Y = -SYMBOL_SIZE * 0.02;
	const AMOUNT_Y = SYMBOL_SIZE * 0.78;
	const CREST_Y = -BOX_H / 2;

	let nowMs = $state(0);
	let born = 0;
	let introStartMs = $state(0); // wordmark drop-in anchor — RESET on every rank-up
	let rankAtMs = $state(-1e9); // last promotion (flash ring + crest re-cut)

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

	// promotion watcher — first run only records the starting tier (the mount intro is
	// already its own ceremony; the stinger belongs to CROSSINGS, not to appearing)
	let shownLevel = -1;
	$effect(() => {
		const lvl = displayLevel;
		if (shownLevel === -1) {
			shownLevel = lvl;
			return;
		}
		if (lvl !== shownLevel) {
			const promoted = lvl > shownLevel;
			shownLevel = lvl;
			if (promoted) {
				introStartMs = performance.now();
				rankAtMs = performance.now();
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_tier_up' });
			}
		}
	});

	const t = $derived((nowMs - born) / 1000); // seconds since mount (light motion clock)
	const intro = $derived(clamp01((nowMs - introStartMs) / 420)); // word drop progress
	const rankAge = $derived((nowMs - rankAtMs) / 1000); // seconds since last promotion

	const wordScale = $derived.by(() => {
		// anticipation -> impact: drops in oversized, overshoots into place, then breathes
		if (intro < 1) return 1.9 - 0.9 * EASE.impact(intro);
		return 1 + 0.015 * Math.sin(t * Math.PI * 1.6);
	});
	const wordAlpha = $derived(clamp01(intro * 2.2));
	const boxScale = $derived.by(() => {
		// the whole box lands with a quick impact settle, then holds still (the light moves,
		// the architecture doesn't)
		const u = clamp01(t / 0.36);
		return 0.86 + 0.14 * EASE.impact(u);
	});
	// crest re-cut pulse rides the promotion clock (also fires once on mount via born)
	const crestPulse = $derived(1 + 0.32 * Math.sin(Math.PI * clamp01(rankAge / 0.42)));
</script>

<!-- rotating prism rays behind the box (additive, accent-led; MAX = gold storm) -->
<Graphics
	blendMode="add"
	draw={(g) => {
		const R = SYMBOL_SIZE * (4.4 + tier * 0.5);
		const bloom = EASE.settle(clamp01(t / 0.55));
		const spin = t * (0.22 + tier * 0.03) * Math.PI * 2 * 0.1;
		for (let i = 0; i < RAYS; i++) {
			const a0 = spin + (i / RAYS) * Math.PI * 2;
			const w = ((Math.PI * 2) / RAYS) * 0.38;
			const col = isMax ? GOLD : lerpColor(accent, paletteAt(i / RAYS + t * 0.12), 0.25);
			const pulse = 0.6 + 0.4 * Math.sin(t * Math.PI * 1.4 + i * 1.1);
			g.moveTo(0, 0)
				.arc(0, 0, R * bloom, a0 - w / 2, a0 + w / 2)
				.lineTo(0, 0)
				.fill({ color: col, alpha: 0.075 * pulse * bloom });
		}
		// glow bloom behind the plaque centre
		g.circle(0, 0, SYMBOL_SIZE * (2.4 + tier * 0.2) * bloom).fill({
			color: isMax ? GOLD : lerpColor(accent, 0xffffff, 0.35),
			alpha: 0.12 + 0.05 * Math.sin(t * Math.PI * 1.2),
		});
		// MAX WIN gold storm: slow-orbit embers around the plaque (heavier presence at the
		// cap without any new architecture — the full bespoke scene lands with the 10,000x
		// math pass, see POLISH-ROADMAP 1.3)
		if (isMax) {
			for (let k = 0; k < 14; k++) {
				const ang = t * (0.25 + (k % 3) * 0.08) + k * ((Math.PI * 2) / 14);
				const rr = SYMBOL_SIZE * (3.1 + 0.7 * Math.sin(t * 0.9 + k * 2.3)) * bloom;
				const tw = (Math.sin(t * Math.PI * 2.2 + k * 1.7) + 1) / 2;
				g.circle(Math.cos(ang) * rr, Math.sin(ang) * rr * 0.72, 2 + 3 * tw).fill({
					color: GOLD,
					alpha: (0.18 + 0.3 * tw) * bloom,
				});
			}
		}
	}}
/>

<Container scale={boxScale}>
	<PrismPanel width={BOX_W} height={BOX_H} {accent}>
		<!-- soft radial under-glow behind the amount chamber (concentric falloff) -->
		<Graphics
			blendMode="add"
			draw={(g) => {
				const breathe = 0.8 + 0.2 * Math.sin(t * Math.PI * 1.1);
				for (let i = 4; i >= 1; i--) {
					const u = i / 4;
					g.circle(0, AMOUNT_Y, SYMBOL_SIZE * 1.55 * u).fill({
						color: lerpColor(accent, 0xffffff, 0.3),
						alpha: 0.035 * (1.2 - u) * breathe + 0.012,
					});
				}
			}}
		/>

		<!-- wordmark: auto-fit INSIDE the plaque, impact drop-in (re-drops on rank-up) -->
		<Container y={WORD_Y} scale={wordScale} alpha={wordAlpha}>
			<ResponsiveBitmapText
				anchor={0.5}
				maxWidth={WORD_MAX_W}
				text={word}
				style={prismStyle(WORD_SIZE, { align: 'center' })}
			/>
		</Container>

		<!-- divider: accent facet line, centre diamond + small end-cut diamonds -->
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
				g.poly([0, DIVIDER_Y - r, r, DIVIDER_Y, 0, DIVIDER_Y + r, -r, DIVIDER_Y]).fill({
					color: 0xffffff,
					alpha: 0.75,
				});
				const re = 3 + 0.8 * breathe;
				for (const sx of [-1, 1]) {
					g.poly([
						sx * half, DIVIDER_Y - re,
						sx * half + re, DIVIDER_Y,
						sx * half, DIVIDER_Y + re,
						sx * half - re, DIVIDER_Y,
					]).fill({ color: lerpColor(accent, 0xffffff, 0.55), alpha: 0.7 });
				}
			}}
		/>

		<!-- count-up (parent-provided) in the lower chamber -->
		<Container y={AMOUNT_Y}>
			{@render props.children()}
		</Container>

		<!-- TIER CREST — faceted gem seated on the plaque's top edge; re-cuts on rank-up -->
		<Container y={CREST_Y} scale={crestPulse}>
			<Graphics
				draw={(g) => {
					const G = SYMBOL_SIZE * (0.52 + tier * 0.045);
					// halo behind the crest (additive-feel via low-alpha light colour)
					g.circle(0, 0, G * 1.05).fill({
						color: lerpColor(accent, 0xffffff, 0.4),
						alpha: 0.16,
					});
					// silhouette: table -> girdle -> pavilion tip (brilliant-cut profile)
					const crown = [
						-0.42 * G, -0.5 * G,
						0.42 * G, -0.5 * G,
						0.72 * G, -0.08 * G,
						-0.72 * G, -0.08 * G,
					];
					const pavilion = [-0.72 * G, -0.08 * G, 0.72 * G, -0.08 * G, 0, 0.62 * G];
					g.poly(pavilion).fill({ color: lerpColor(accent, 0x140b24, 0.3) });
					g.poly(crown).fill({ color: lerpColor(accent, 0xffffff, 0.18) });
					// centre facets catch the top light
					g.poly([
						-0.26 * G, -0.5 * G,
						0.26 * G, -0.5 * G,
						0.4 * G, -0.08 * G,
						-0.4 * G, -0.08 * G,
					]).fill({ color: lerpColor(accent, 0xffffff, 0.45) });
					g.poly([-0.3 * G, -0.08 * G, 0.3 * G, -0.08 * G, 0, 0.48 * G]).fill({
						color: lerpColor(accent, 0xffffff, 0.12),
						alpha: 0.9,
					});
					// outline + glint
					g.poly([
						-0.42 * G, -0.5 * G,
						0.42 * G, -0.5 * G,
						0.72 * G, -0.08 * G,
						0, 0.62 * G,
						-0.72 * G, -0.08 * G,
					]).stroke({ width: 1.4, color: 0xffffff, alpha: 0.55, join: 'miter' });
					g.moveTo(-0.3 * G, -0.42 * G)
						.lineTo(0.05 * G, -0.42 * G)
						.stroke({ width: 1.6, color: 0xffffff, alpha: 0.8, cap: 'round' });
				}}
			/>
		</Container>
	</PrismPanel>
</Container>

<!-- promotion flash ring — expands from the plaque on every rank-up, over everything -->
{#if rankAge < 0.62}
	<Graphics
		blendMode="add"
		draw={(g) => {
			const u = clamp01(rankAge / 0.62);
			const e = EASE.settle(u);
			g.circle(0, 0, SYMBOL_SIZE * (0.9 + 3.1 * e)).stroke({
				width: 2 + 9 * (1 - u),
				color: lerpColor(0xffffff, accent, u),
				alpha: 0.55 * (1 - u),
			});
		}}
	/>
{/if}
