<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';

	import { prismNumStyle, fitFontSize } from '../game/fonts';
	import { CELL_W, SYMBOL_SIZE } from '../game/constants';
	import { EASE } from '../game/motion';

	type Props = {
		x: number;
		y: number;
		multiplier: number;
		sticky: boolean;
	};

	const props: Props = $props();

	// fitFontSize caps the label to the chip's inner width, so overlap-grown values
	// ("128X") shrink to fit instead of flooding over the square
	const label = $derived(`${props.multiplier}X`);
	const fontSize = $derived(
		fitFontSize(label, props.sticky ? 34 : 50, props.sticky ? SYMBOL_SIZE * 0.62 : CELL_W * 0.76),
	);

	// clean subtle pop-in whenever the value appears or grows (overlap x2 -> x6).
	// Initialized at the pop's START pose — initializing at rest painted one full-size
	// frame before the first rAF tick (a visible flash at mount).
	let badgeScale = $state(0.7);
	let badgeAlpha = $state(0);
	$effect(() => {
		const m = props.multiplier;
		if (!m) return;
		badgeScale = 0.7;
		badgeAlpha = 0;
		let lastT = performance.now();
		let el = 0;
		let raf = 0;
		const POP_MS = 240;
		const frame = () => {
			const t = performance.now();
			el += t - lastT;
			lastT = t;
			const u = Math.min(1, el / POP_MS);
			badgeScale = 0.7 + 0.3 * EASE.impact(u);
			badgeAlpha = Math.min(1, u * 3);
			if (u < 1) raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});
</script>

<Container x={props.x} y={props.y} scale={badgeScale} alpha={badgeAlpha}>
	<BitmapText anchor={0.5} text={label} style={prismNumStyle(fontSize)} />
</Container>
