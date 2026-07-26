<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventFreeSpinOutro =
		| { type: 'freeSpinOutroShow' }
		| { type: 'freeSpinOutroHide' }
		| { type: 'freeSpinOutroCountUp'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	// Feature finale — TOTAL WIN presented with the same layered WinBox light show as the
	// big wins (one visual language), plus the prism-shard burst. No template spines/sprites.
	import { FadeContainer, WinCountUpProvider, ResponsiveBitmapText } from 'components-pixi';
	import {
		bookEventAmountToBetAmountMultiplier,
		bookEventAmountToCurrencyString,
	} from 'utils-shared/amount';
	import { waitForResolve } from 'utils-shared/wait';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';
	import { Container } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import WinBox from './WinBox.svelte';
	import PrismShards from './PrismShards.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	// starts HIDDEN like every other overlay — init true made the first feature's TOTAL WIN
	// panel hard-cut in (FadeContainer had already tweened to alpha 1 invisibly at boot)
	let show = $state(false);
	let amount = $state(0);
	let winLevelData = $state<WinLevelData>();
	let oncomplete = $state(() => {});
	let onCountUpComplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		freeSpinOutroShow: () => (show = true),
		freeSpinOutroHide: async () => (show = false),
		freeSpinOutroCountUp: async (emitterEvent) => {
			amount = emitterEvent.amount;
			winLevelData = emitterEvent.winLevelData;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	{#if winLevelData}
		<!-- same >10x rule as Win.svelte: only totals above 10x the bet earn the roll — a
		     small feature total lands instantly (the panel + press-to-continue still hold) -->
		{@const duration =
			bookEventAmountToBetAmountMultiplier(amount) > 10
				? Math.max(winLevelData.presentDuration, 2500)
				: 0}
		{@const boxLevel = Math.max(6, winLevelData.level)}
		<WinCountUpProvider {amount} {duration} oncomplete={() => onCountUpComplete()}>
			{#snippet children({ countUpAmount, startCountUp, finishCountUp, countUpCompleted })}
				<OnMount onmount={() => startCountUp()} />

				<CanvasSizeRectangle backgroundColor={0x05030a} backgroundAlpha={0.6} />

				<MainContainer>
					<Container
						x={context.stateGameDerived.boardLayout().x}
						y={context.stateGameDerived.boardLayout().y}
					>
						<WinBox level={boxLevel} text="TOTAL WIN">
							<ResponsiveBitmapText
								anchor={0.5}
								maxWidth={SYMBOL_SIZE * 4.6}
								text={bookEventAmountToCurrencyString(countUpAmount)}
								style={prismStyle(SYMBOL_SIZE * 1.5, { align: 'center', letterSpacing: 0 })}
							/>
						</WinBox>
					</Container>
				</MainContainer>

				<PrismShards emit={!countUpCompleted} levelAlias={winLevelData?.alias} />

				<!-- unmount the full-screen catcher the instant hiding starts — an invisible
				     fading rect must not swallow board presses -->
				{#if show}
					<PressToContinue onpress={() => (countUpCompleted ? oncomplete() : finishCountUp())} />
				{/if}
			{/snippet}
		</WinCountUpProvider>
	{/if}
</FadeContainer>
