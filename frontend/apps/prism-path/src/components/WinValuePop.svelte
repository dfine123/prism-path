<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';

	import { prismStyle } from '../game/fonts';
	import { stateWinPop, POP_FONT, MULT_FONT } from '../game/stateWinPop.svelte';
</script>

<!-- the line's WIN VALUE: bare number pops at the centroid on the sweep's impact frame;
     its beast multiplier pops beneath, then collapses in as the value rolls to the total.
     Mounted ABOVE the multiplier-badge layer — the headline always reads. -->
{#if stateWinPop.alpha > 0.01}
	<Container x={stateWinPop.x} y={stateWinPop.y} scale={stateWinPop.scale} alpha={stateWinPop.alpha}>
		<BitmapText anchor={0.5} text={stateWinPop.label} style={prismStyle(POP_FONT)} />
		{#if stateWinPop.multLabel && stateWinPop.multAlpha > 0.01}
			<Container y={stateWinPop.multY} scale={stateWinPop.multScale} alpha={stateWinPop.multAlpha}>
				<BitmapText anchor={0.5} text={stateWinPop.multLabel} style={prismStyle(MULT_FONT)} />
			</Container>
		{/if}
	</Container>
{/if}
