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
	import { stateBet } from 'state-shared';
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
		// press (reveal also breathes, for pressless spins; the refractory guard dedupes).
		// ONLY when idle: mid-round the same press means STOP, and a launch-anticipation
		// breath on a stop press reads as a glitch.
		soundPressBet: () => {
			if (context.stateXstateDerived.isIdle()) boardBreathe();
		},
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

	// QUICK-SPIN SLAM (operator): engaging turbo MID-FLIGHT of a paced spin lands
	// every reel together — without this, a space quick-spin sped up everything
	// except the reels, which kept their full one-by-one stagger ("weirdly falling
	// in"). Guarded to paced spin types so a spin STARTED under turbo keeps its
	// designed fast timing instead of being slammed at launch.
	$effect(() => {
		if (!stateBet.isTurbo) return;
		const midPacedFlight = context.stateGame.board.some(
			(reel) =>
				reel.reelState.motion === 'spinning' &&
				(reel.reelState.spinType === 'normal' || reel.reelState.spinType === 'anticipated'),
		);
		if (midPacedFlight) context.stateGameDerived.enhancedBoard.stop();
	});
</script>

{#if show}
	<BoardContext animate={false}>
		<BoardContainer>
			<BoardMask />
			<!-- Z-ORDER SANDWICH (operator): dragon PATH trail cells render FIRST, the
			     win-line ribbon rides OVER the path, and every other symbol renders
			     over the ribbon (multiplier badges + value pops top everything in the
			     animate layer's masked container). Masked so lines still slide out
			     from under the frame border. -->
			<BoardBase only="trail" />
			<Container>
				<Rectangle
					isMask
					width={context.stateGameDerived.boardLayout().width}
					height={context.stateGameDerived.boardLayout().height}
				/>
				<WinLines />
			</Container>
			<BoardBase only="nonTrail" />
		</BoardContainer>
	</BoardContext>

	<BoardContext animate={true}>
		<BoardContainer>
			<BoardBase />
			<StickyDragonMarkers />
			<!-- the dragon flight clips EXACTLY at the board rect: it exits THROUGH the
			     board edge, disappearing under the border (never flying over the frame
			     art). Layer order: flight < MULTIPLIER BADGES < value pop — a badge is
			     never buried under a path, and the headline value tops everything. -->
			<Container>
				<Rectangle
					isMask
					width={context.stateGameDerived.boardLayout().width}
					height={context.stateGameDerived.boardLayout().height}
				/>
				<PrismBeastTravel />
				<MultiplierBadges />
				<WinValuePop />
			</Container>
		</BoardContainer>
	</BoardContext>
{/if}
