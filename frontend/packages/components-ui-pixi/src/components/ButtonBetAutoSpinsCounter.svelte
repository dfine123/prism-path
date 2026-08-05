<script lang="ts">
	// Remaining-spins readout ON the autoplay button face: crystal glass core (not the
	// template's raw black Rectangle) with the count in the console voice. Sized in
	// SUPER_UI.btn space — the parent scales for other button sizes.
	import { Text } from 'pixi-svelte';
	import { stateBet } from 'state-shared';

	import UiGlass from './UiGlass.svelte';
	import { SUPER_UI } from '../theme';

	const T = SUPER_UI;
	const D = T.btn * 0.78;
	const fontSize = $derived.by(() => {
		if (stateBet.autoSpinsCounter === Infinity) return D * 0.52;
		if (stateBet.autoSpinsCounter > 99) return D * 0.34;
		if (stateBet.autoSpinsCounter > 9) return D * 0.42;
		return D * 0.5;
	});
</script>

{#if stateBet.autoSpinsCounter > 0}
	<UiGlass width={D} height={D} radius={D / 2} accent={T.color.gold} />
	<Text
		anchor={0.5}
		text={stateBet.autoSpinsCounter === Infinity ? '∞' : stateBet.autoSpinsCounter}
		style={{
			fontFamily: T.font,
			fill: T.color.gold,
			fontWeight: '700',
			fontSize,
		}}
	/>
{/if}
