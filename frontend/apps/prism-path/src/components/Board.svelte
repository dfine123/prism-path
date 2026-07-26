<script lang="ts" module>
	import type { RawSymbol, Position } from '../game/types';

	export type EmitterEventBoard =
		| { type: 'boardSettle'; board: RawSymbol[][] }
		| { type: 'boardShow' }
		| { type: 'boardHide' }
		| {
				type: 'boardWithAnimateSymbols';
				symbolPositions: Position[];
		  };
</script>

<script lang="ts">
	import { waitForResolve } from 'utils-shared/wait';
	import { BoardContext } from 'components-shared';
	import { Container, Rectangle } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { boardBreathe } from '../game/stateFx.svelte';
	import BoardContainer from './BoardContainer.svelte';
	import BoardMask from './BoardMask.svelte';
	import BoardBase from './BoardBase.svelte';
	import PrismBeastTravel from './PrismBeastTravel.svelte';
	import StickyDragonMarkers from './StickyDragonMarkers.svelte';
	import WinLines from './WinLines.svelte';
	import MultiplierBadges from './MultiplierBadges.svelte';
	import WinValuePop from './WinValuePop.svelte';

	const context = getContext();

	let show = $state(true);

	context.eventEmitter.subscribeOnMount({
		// the board reacts to the CLICK itself — instant tactile acknowledgment of the spin
		// press (reveal also breathes, for pressless spins; the refractory guard dedupes)
		soundPressBet: () => boardBreathe(),
		stopButtonClick: () => context.stateGameDerived.enhancedBoard.stop(),
		boardSettle: ({ board }) => context.stateGameDerived.enhancedBoard.settle(board),
		boardShow: () => (show = true),
		boardHide: () => (show = false),
		boardWithAnimateSymbols: async ({ symbolPositions }) => {
			const getPromises = () =>
				symbolPositions.map(async (position) => {
					const reelSymbol = context.stateGame.board[position.reel].reelState.symbols[position.row];
					reelSymbol.symbolState = 'win';
					await waitForResolve((resolve) => (reelSymbol.oncomplete = resolve));
					reelSymbol.symbolState = 'postWinStatic';
				});

			await Promise.all(getPromises());
		},
	});

	context.stateGameDerived.enhancedBoard.readyToSpinEffect();
</script>

{#if show}
	<BoardContext animate={false}>
		<BoardContainer>
			<BoardMask />
			<BoardBase />
		</BoardContainer>
	</BoardContext>

	<BoardContext animate={true}>
		<BoardContainer>
			<BoardBase />
			<StickyDragonMarkers />
			<!-- win lines AND the dragon flight clip EXACTLY at the board rect: lines slide out
			     from UNDER the frame border, and the dragon exits THROUGH the board edge,
			     disappearing under the border (never flying over the frame art).
			     Layer order inside the mask: ribbon < flight < MULTIPLIER BADGES < value pop —
			     a badge is never buried under a path, and the headline value tops everything. -->
			<Container>
				<Rectangle
					isMask
					width={context.stateGameDerived.boardLayout().width}
					height={context.stateGameDerived.boardLayout().height}
				/>
				<WinLines />
				<PrismBeastTravel />
				<MultiplierBadges />
				<WinValuePop />
			</Container>
		</BoardContainer>
	</BoardContext>
{/if}
