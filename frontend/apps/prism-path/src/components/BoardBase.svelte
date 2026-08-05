<script lang="ts">
	import ReelSymbol from './ReelSymbol.svelte';
	import { getContext } from '../game/context';
	import type { RawSymbol } from '../game/types';

	// `only` splits the board into TWO passes around the win-line ribbon (operator:
	// the line renders IN FRONT of a dragon's path cells but behind every other
	// symbol and the multiplier badges): 'trail' = path trail cells, 'nonTrail' =
	// everything else. Omit for the single-pass animate layer.
	type Props = { only?: 'trail' | 'nonTrail' };
	const props: Props = $props();
	const context = getContext();

	// mirrors Symbol.svelte's isTrailWild: a flight-converted wild (or a vacated
	// sticky seat) renders as the animated prism trail
	const isTrail = (raw: RawSymbol) => {
		if (raw.name !== 'WILD' || !raw.direction) return false;
		if (raw.sticky) return !!raw.dormant;
		return !!raw.trail;
	};
	const passes = (raw: RawSymbol) =>
		props.only === undefined || (props.only === 'trail') === isTrail(raw);
</script>

{#each context.stateGame.board as reel, reelIndex (reelIndex)}
	{#each reel.reelState.symbols as reelSymbol}
		{#if passes(reelSymbol.rawSymbol)}
			<ReelSymbol {reelIndex} {reelSymbol} />
		{/if}
	{/each}
{/each}
