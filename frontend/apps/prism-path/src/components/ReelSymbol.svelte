<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Container } from 'pixi-svelte';

	import Symbol from './Symbol.svelte';
	import SymbolWrap from './SymbolWrap.svelte';
	import { getSymbolInfo, getSymbolX } from '../game/utils';
	import { stateFx } from '../game/stateFx.svelte';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import type { ReelSymbol } from '../game/stateGame.svelte';

	type Props = {
		reelIndex: number;
		reelSymbol: ReelSymbol;
	};

	const props: Props = $props();
	const symbolInfo = $derived(
		getSymbolInfo({ rawSymbol: props.reelSymbol.rawSymbol, state: props.reelSymbol.symbolState }),
	);

	// HIT SWELL: an extra expand on top of the sprite's own win reaction (operator:
	// slightly increase the symbol react on hit). One clean swell, then back to 1 —
	// driven by the shared trail clock, acquired only while this symbol is winning.
	// SCALED-TIME contract: accumulate el += dt * winSpeed per frame (like the other
	// paced surfaces) — multiplying total elapsed by the CURRENT winSpeed made the
	// scale JUMP on the exact skip-click that should feel responsive.
	let holdingClock = false;
	let swellEl = $state(0);
	let lastT = 0;
	$effect(() => {
		const isWin = props.reelSymbol.symbolState === 'win';
		if (isWin && !holdingClock) {
			holdingClock = true;
			swellEl = 0;
			lastT = 0;
			acquireTrailClock();
		} else if (!isWin && holdingClock) {
			holdingClock = false;
			releaseTrailClock();
		}
	});
	$effect(() => {
		if (!holdingClock) return;
		const t = trailClock.t;
		if (lastT !== 0) swellEl += (t - lastT) * 1000 * stateFx.winSpeed;
		lastT = t;
	});
	onDestroy(() => {
		if (holdingClock) releaseTrailClock();
	});
	const hitScale = $derived.by(() => {
		if (props.reelSymbol.symbolState !== 'win') return 1;
		const u = Math.min(1, Math.max(0, swellEl / 550));
		return 1 + 0.1 * Math.sin(Math.PI * u);
	});
</script>

<SymbolWrap
	x={getSymbolX(props.reelIndex)}
	y={props.reelSymbol.symbolY()}
	animating={symbolInfo.type === 'spine' &&
		(props.reelSymbol.symbolState === 'land' || props.reelSymbol.symbolState === 'win')}
>
	<Container scale={hitScale}>
		<Symbol
			state={props.reelSymbol.symbolState}
			rawSymbol={props.reelSymbol.rawSymbol}
			oncomplete={() => {
				if (props.reelSymbol.symbolState === 'win') props.reelSymbol.oncomplete();
				if (props.reelSymbol.symbolState === 'land') props.reelSymbol.symbolState = 'static';
			}}
		/>
	</Container>
</SymbolWrap>
