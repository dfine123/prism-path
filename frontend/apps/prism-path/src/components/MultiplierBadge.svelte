<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';

	import { prismStyle } from '../game/fonts';
	import { EASE } from '../game/motion';

	type Props = {
		x: number;
		y: number;
		multiplier: number;
		sticky: boolean;
	};

	const props: Props = $props();

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
	<BitmapText anchor={0.5} text={`${props.multiplier}X`} style={prismStyle(props.sticky ? 34 : 50)} />
</Container>
