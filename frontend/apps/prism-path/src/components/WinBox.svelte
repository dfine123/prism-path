<script lang="ts">
	// Code-first, layered win box (studio-motion-canon: "win boxes — layered, code-first,
	// additive"). No baked clips: a STACK of parametric layers — rotating light rays, prism
	// glow bloom, Prism-font wordmark, sparkle field — with the count-up rendered beneath by
	// the parent. Tiers escalate ADDITIVELY (more rays, bigger word, hotter glow, gold shift
	// at max) — the box never swaps to a different design between tiers.
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { EASE, clamp01, paletteAt, lerpColor } from '../game/motion';

	type Props = {
		level: number; // 6..10 (big..max)
		text: string; // wordmark: BIG WIN / SUPER WIN / ...
		children: Snippet;
	};
	const props: Props = $props();

	// ---- tier ladder (additive escalation) ----
	const tier = $derived(Math.max(0, Math.min(4, props.level - 6))); // 0..4
	const RAYS = $derived(8 + tier * 2);
	const WORD_SIZE = $derived(SYMBOL_SIZE * (1.5 + tier * 0.14));
	const GOLD = 0xffd25e;
	const isMax = $derived(props.level >= 10);

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
		return 1 + 0.02 * Math.sin(t * Math.PI * 1.6);
	});
	const wordAlpha = $derived(clamp01(intro * 2.2));
</script>

<!-- rotating prism rays (additive) -->
<Graphics
	blendMode="add"
	draw={(g) => {
		const R = SYMBOL_SIZE * (4.4 + tier * 0.5);
		const bloom = EASE.settle(clamp01(t / 0.55));
		const spin = t * (0.22 + tier * 0.03) * Math.PI * 2 * 0.1;
		for (let i = 0; i < RAYS; i++) {
			const a0 = spin + (i / RAYS) * Math.PI * 2;
			const w = (Math.PI * 2) / RAYS * 0.38;
			const col = isMax ? GOLD : paletteAt(i / RAYS + t * 0.12);
			const pulse = 0.6 + 0.4 * Math.sin(t * Math.PI * 1.4 + i * 1.1);
			g.moveTo(0, 0)
				.arc(0, 0, R * bloom, a0 - w / 2, a0 + w / 2)
				.lineTo(0, 0)
				.fill({ color: col, alpha: 0.075 * pulse * bloom });
		}
		// central glow bloom behind the wordmark
		const glowCol = isMax ? GOLD : lerpColor(paletteAt(t * 0.15), 0xffffff, 0.35);
		g.circle(0, -SYMBOL_SIZE * 1.1, SYMBOL_SIZE * (2.1 + tier * 0.2) * bloom).fill({
			color: glowCol,
			alpha: 0.13 + 0.05 * Math.sin(t * Math.PI * 1.2),
		});
		g.circle(0, -SYMBOL_SIZE * 1.1, SYMBOL_SIZE * (1.15 + tier * 0.12) * bloom).fill({
			color: 0xffffff,
			alpha: 0.1 + 0.04 * Math.sin(t * Math.PI * 1.7),
		});
		// sparkle field (deterministic twinkle ring around the box)
		for (let k = 0; k < 10 + tier * 3; k++) {
			const ang = (k / (10 + tier * 3)) * Math.PI * 2 + t * 0.25;
			const rad = SYMBOL_SIZE * (2.4 + 0.5 * Math.sin(t * 1.3 + k * 2.2));
			const tw = (Math.sin(t * Math.PI * 3.1 + k * 1.7) + 1) / 2;
			g.circle(Math.cos(ang) * rad, -SYMBOL_SIZE * 1.1 + Math.sin(ang) * rad * 0.55, 1.6 + 2.2 * tw).fill({
				color: isMax ? GOLD : 0xffffff,
				alpha: (0.2 + 0.5 * tw) * EASE.settle(clamp01(t / 0.8)),
			});
		}
	}}
/>

<!-- wordmark: impact drop-in, then breathe -->
<Container y={-SYMBOL_SIZE * 1.15} scale={wordScale} alpha={wordAlpha}>
	<BitmapText anchor={0.5} text={props.text} style={prismStyle(WORD_SIZE, { align: 'center' })} />
</Container>

<!-- count-up (parent-provided) beneath the wordmark -->
<Container y={SYMBOL_SIZE * 0.55}>
	{@render props.children()}
</Container>
