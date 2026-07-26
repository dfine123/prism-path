<script lang="ts">
	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE, BOARD_DIMENSIONS } from '../game/constants';
	import MultiplierBadge from './MultiplierBadge.svelte';

	// DEDICATED BADGE LAYER: multiplier numbers used to render inside each cell, where the
	// dragon's in-flight ribbon and the win-line ribbon (drawn later in the overlay stack)
	// covered them. Hoisted here — mounted AFTER the trail cells, the flight overlay and the
	// win ribbon, BEFORE the win value pop — so a badge is never buried under a path.
	// A STICKY dragon's badge sits by its path edge (bottom of the cell), never covering
	// the seated dragon; trail cells keep the centred badge.
	const context = getContext();

	const top = 0;
	const bottom = SYMBOL_SIZE * BOARD_DIMENSIONS.y;

	const badges = $derived(
		context.stateGame.board.flatMap((reel, reelIndex) =>
			reel.reelState.symbols
				.filter((reelSymbol) => (reelSymbol.rawSymbol.multiplier ?? 0) > 0)
				.map((reelSymbol) => {
					const sticky = !!reelSymbol.rawSymbol.sticky;
					return {
						id: reelSymbol.id,
						x: getSymbolX(reelIndex),
						y: reelSymbol.symbolY() + (sticky ? SYMBOL_SIZE * 0.31 : 0),
						baseY: reelSymbol.symbolY(),
						multiplier: reelSymbol.rawSymbol.multiplier as number,
						sticky,
					};
				})
				.filter((b) => b.baseY >= top && b.baseY <= bottom),
		),
	);
</script>

{#each badges as badge (badge.id)}
	<MultiplierBadge x={badge.x} y={badge.y} multiplier={badge.multiplier} sticky={badge.sticky} />
{/each}
