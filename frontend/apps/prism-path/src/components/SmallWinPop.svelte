<script lang="ts">
	// Small-win amount with the standard impact vocabulary: quick pop-in
	// (EASE.impact), soft settle, gentle breathe while it holds. The audit flagged
	// the old static paint as the one value in the game that landed with no beat.
	import { onMount } from 'svelte';
	import { Container } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { EASE, clamp01 } from '../game/motion';

	type Props = {
		amount: number;
		maxWidth: number;
	};
	const props: Props = $props();

	let born = 0;
	let t = $state(0);
	onMount(() => {
		born = performance.now();
		let raf = 0;
		const frame = () => {
			t = (performance.now() - born) / 1000;
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	const popScale = $derived.by(() => {
		const u = clamp01(t / 0.32);
		if (u < 1) return 1.7 - 0.7 * EASE.impact(u);
		return 1 + 0.012 * Math.sin(t * Math.PI * 1.5);
	});
	const alpha = $derived(clamp01(t / 0.12));
</script>

<Container scale={popScale} {alpha}>
	<ResponsiveBitmapText
		anchor={0.5}
		maxWidth={props.maxWidth}
		text={bookEventAmountToCurrencyString(props.amount)}
		style={prismStyle(SYMBOL_SIZE, { align: 'center', letterSpacing: 0 })}
	/>
</Container>
