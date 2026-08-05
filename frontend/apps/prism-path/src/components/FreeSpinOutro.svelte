<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventFreeSpinOutro =
		| { type: 'freeSpinOutroShow' }
		| { type: 'freeSpinOutroHide' }
		| { type: 'freeSpinOutroCountUp'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	// Feature finale ON THE WIN-BOX PLAQUE (operator: every stone/frame-derived
	// panel failed — the progressive gem plaque is the game's ONE approved dialog
	// design, so the ceremonies join its family). WinBox at level 9 with a GOLD
	// accent override: opaque violet plaque, corner gems, crest with side stones
	// and crown, gold gem rain — "FREE SPINS COMPLETE" fixed wordmark, static
	// total with one impact beat. Shard burst behind, press to return.
	import { onMount } from 'svelte';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';
	import { BitmapText, Container } from 'pixi-svelte';
	import { ResponsiveBitmapText, FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01 } from '../game/motion';
	import { boardFocusTo } from '../game/stateFx.svelte';
	import WinBox from './WinBox.svelte';
	import PrismShards from './PrismShards.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	const GOLD = 0xffd25e;
	// the WinBox plaque geometry (its BOX_H is 3.6 symbols; invite seats just under)
	const BOX_H = SYMBOL_SIZE * 3.6;

	// "(bonus name) COMPLETE": bought features carry their card title; a naturally
	// triggered (or hunt-found) feature is plainly FREE SPINS
	const bonusName = $derived.by(() => {
		const mode = stateBetDerived.activeBetMode() as { type?: string; title?: string } | null;
		return mode?.type === 'buy' && mode.title ? mode.title : 'FREE SPINS';
	});

	let show = $state(false);
	let amount = $state(0);
	let oncomplete = $state(() => {});
	let shownAtMs = 0;
	let nowMs = $state(0);

	onMount(() => {
		let raf = 0;
		const frame = () => {
			nowMs = performance.now();
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	context.eventEmitter.subscribeOnMount({
		freeSpinOutroShow: () => {
			shownAtMs = performance.now();
			show = true;
		},
		freeSpinOutroHide: async () => (show = false),
		freeSpinOutroCountUp: async (emitterEvent) => {
			amount = emitterEvent.amount;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});

	// camera focus while the panel holds (same as the big-win box)
	$effect(() => {
		boardFocusTo(show ? 1 : 0);
	});

	const secs = $derived(nowMs / 1000);
	const age = $derived(show ? (nowMs - shownAtMs) / 1000 : 0);
	const labelIn = $derived(clamp01((age - 0.24) / 0.3));
	// the amount lands STATIC with one impact beat, then settles to 1 and breathes
	// WITH the plaque (its own idle sine read as the amount and box alternating)
	const amountIn = $derived(clamp01((age - 0.38) / 0.32));
	const amountScale = $derived.by(() => (amountIn < 1 ? 2.0 - 1.0 * EASE.impact(amountIn) : 1));
	// the shard burst is the celebration garnish: a short eruption as the panel lands
	const bursting = $derived(show && age < 1.4);
</script>

<FadeContainer {show}>
	{#if show}
		<!-- manual play holds on PRESS TO CONTINUE; AUTOPLAY / SPACE-HOLD auto-advance
		     after a readable hold. Generation-guarded. -->
		<OnMount
			onmount={async () => {
				const myResolve = oncomplete;
				if (stateBetDerived.hasAutoBetCounter() || stateBet.isSpaceHold) {
					await waitForTimeout(1700);
					if (oncomplete === myResolve) oncomplete();
				}
			}}
		/>

		<CanvasSizeRectangle backgroundColor={0x05030a} backgroundAlpha={0.6} />

		<!-- shards UNDER the plaque: gems erupt from behind, never over text -->
		<PrismShards emit={bursting} levelAlias="big" />

		<MainContainer>
			<Container
				x={context.stateGameDerived.boardLayout().x}
				y={context.stateGameDerived.boardLayout().y}
			>
				<!-- THE plaque: the approved win-box family, gold ceremony trim
				     (corner gems, crest + side stones + crown, gold gem rain) -->
				<WinBox level={9} accentOverride={GOLD} fixedText={`${bonusName} COMPLETE`}>
					<Container y={-SYMBOL_SIZE * 0.52} alpha={labelIn}>
						<BitmapText
							anchor={0.5}
							text="TOTAL WIN:"
							style={superLabelStyle(SYMBOL_SIZE * 0.28, { align: 'center' })}
						/>
					</Container>
					<Container scale={amountScale} alpha={clamp01(amountIn * 2.4)}>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={SYMBOL_SIZE * 4.4}
							text={bookEventAmountToCurrencyString(amount)}
							style={prismStyle(SYMBOL_SIZE * 1.0, { align: 'center', letterSpacing: 0 })}
						/>
					</Container>
				</WinBox>

				<!-- the invite, seated with the plaque -->
				<BitmapText
					anchor={0.5}
					y={BOX_H / 2 + SYMBOL_SIZE * 0.34}
					text="PRESS ANYWHERE TO CONTINUE"
					alpha={(0.62 + 0.38 * (Math.sin(secs * Math.PI * 1.3) + 1) * 0.5) *
						clamp01((age - 0.7) / 0.35)}
					style={superLabelStyle(SYMBOL_SIZE * 0.185, { align: 'center' })}
				/>
			</Container>
		</MainContainer>

		<PressToContinue showLabel={false} onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
