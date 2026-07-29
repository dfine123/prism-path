<script lang="ts">
	// FORMATTED win box — one cut-crystal plaque CONTAINS the whole statement: wordmark
	// (auto-fit to the plaque, never screen-wide), divider, count-up amount. The gem-shard
	// burst renders BEHIND this box (consumers order it under), erupting out around the
	// plaque edges — text is always clean on top. Tiers escalate ADDITIVELY (accent colour,
	// rays, word size) — the box never swaps to a different design between tiers.
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';

	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { EASE, clamp01, paletteAt, lerpColor } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';

	type Props = {
		level: number; // 6..10 (big..max)
		text: string; // wordmark: BIG WIN / SUPER WIN / ...
		children: Snippet;
	};
	const props: Props = $props();

	// ---- tier ladder (additive escalation) ----
	const tier = $derived(Math.max(0, Math.min(4, props.level - 6))); // 0..4
	const RAYS = $derived(8 + tier * 2);
	const WORD_SIZE = $derived(SYMBOL_SIZE * (1.1 + tier * 0.1));
	const GOLD = 0xffd25e;
	const isMax = $derived(props.level >= 10);
	// tier accent ascends the game's own spectrum: cyan -> teal -> violet -> pink -> GOLD.
	// Every light in the box (rays, bloom, plaque shimmer, divider) takes the accent, so
	// each tier reads as one colour statement instead of a random rainbow.
	const ACCENTS = [0x2bb8e8, 0x34c0a1, 0x9b3ce8, 0xff5db1, GOLD] as const;
	const accent = $derived(ACCENTS[tier]);

	// the box: everything lives inside this footprint
	const BOX_W = SYMBOL_SIZE * 6.2;
	const BOX_H = SYMBOL_SIZE * 3.6;
	const WORD_MAX_W = BOX_W - SYMBOL_SIZE * 0.9;
	const WORD_Y = -SYMBOL_SIZE * 0.88;
	const DIVIDER_Y = -SYMBOL_SIZE * 0.1;

	let t = $state(0); // seconds since mount
	let intro = $state(0); // 0..1 wordmark drop-in progress

	onMount(() => {
		const start = performance.now();
		let raf = 0;
		const frame = () => {
			t = (performance.now() - start) / 1000;
			intro = clamp01((performance.now() - start) / 420);
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

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
</script>

<!-- rotating prism rays behind the box (additive, accent-led) -->
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
	}}
/>

<Container scale={boxScale}>
	<PrismPanel width={BOX_W} height={BOX_H} {accent}>
		<!-- wordmark: auto-fit INSIDE the plaque (never wider than the box), impact drop-in -->
		<Container y={WORD_Y} scale={wordScale} alpha={wordAlpha}>
			<ResponsiveBitmapText
				anchor={0.5}
				maxWidth={WORD_MAX_W}
				text={props.text}
				style={prismStyle(WORD_SIZE, { align: 'center' })}
			/>
		</Container>

		<!-- divider: accent facet line with a centre diamond, separating word from amount -->
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
			}}
		/>

		<!-- count-up (parent-provided) in the lower chamber -->
		<Container y={SYMBOL_SIZE * 0.72}>
			{@render props.children()}
		</Container>
	</PrismPanel>
</Container>
