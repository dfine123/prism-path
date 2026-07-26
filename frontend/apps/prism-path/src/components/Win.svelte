<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventWin =
		| { type: 'winShow' }
		| { type: 'winHide' }
		| { type: 'winUpdate'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	import { Container } from 'pixi-svelte';
	import { FadeContainer, WinCountUpProvider, ResponsiveBitmapText } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import {
		bookEventAmountToBetAmountMultiplier,
		bookEventAmountToCurrencyString,
	} from 'utils-shared/amount';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';

	import PrismShards from './PrismShards.svelte';
	import WinBox from './WinBox.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getContext } from '../game/context';
	import { prismStyle } from '../game/fonts';

	const context = getContext();

	let show = $state(false);
	let amount = $state(0);
	let winLevelData = $state<WinLevelData>();
	let oncomplete = $state(() => {});
	let onCountUpComplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		winShow: () => (show = true),
		winHide: () => (show = false),
		winUpdate: async (emitterEvent) => {
			amount = emitterEvent.amount;
			winLevelData = emitterEvent.winLevelData;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	{#if winLevelData}
		{@const isBigWin = winLevelData.type === 'big'}
		<!-- the count-up ROLL is a >10x ceremony: at or under 10x the bet, the amount lands
		     instantly (duration 0) and just holds long enough to read -->
		{@const rollsUp = bookEventAmountToBetAmountMultiplier(amount) > 10}
		{@const duration = rollsUp ? winLevelData.presentDuration : 0}
		<WinCountUpProvider {amount} {duration} oncomplete={() => onCountUpComplete()}>
			{#snippet children({ countUpAmount, startCountUp, finishCountUp, countUpCompleted })}
				{#if isBigWin}
					<!-- dim veil scales with tier (escalation ladder: banner+dim >= big) -->
					<CanvasSizeRectangle
						backgroundColor={0x05030a}
						backgroundAlpha={0.42 + (winLevelData.level - 6) * 0.06}
					/>
				{/if}

				<OnMount
					onmount={async () => {
						await startCountUp();
						// an instant amount needs a longer static hold than a rolled one — the
						// roll itself was the reading time
						await waitForTimeout(rollsUp ? 300 : 650);
						oncomplete();
					}}
				/>

				<MainContainer>
					<Container
						x={context.stateGameDerived.boardLayout().x}
						y={context.stateGameDerived.boardLayout().y}
					>
						{#if isBigWin && winLevelData.text}
							<WinBox level={winLevelData.level} text={winLevelData.text}>
								<ResponsiveBitmapText
									anchor={0.5}
									maxWidth={SYMBOL_SIZE * 4.6}
									text={bookEventAmountToCurrencyString(countUpAmount)}
									style={prismStyle(SYMBOL_SIZE * 1.5, { align: 'center', letterSpacing: 0 })}
								/>
							</WinBox>
						{:else}
							<ResponsiveBitmapText
								anchor={0.5}
								maxWidth={context.stateLayoutDerived.canvasSizes().width /
									context.stateLayoutDerived.mainLayout().scale}
								text={bookEventAmountToCurrencyString(countUpAmount)}
								style={prismStyle(SYMBOL_SIZE, { align: 'center', letterSpacing: 0 })}
							/>
						{/if}
					</Container>
				</MainContainer>

				<PrismShards emit={!countUpCompleted} levelAlias={winLevelData?.alias} />

				<PressToContinue onpress={() => (countUpCompleted ? oncomplete() : finishCountUp())} />
			{/snippet}
		</WinCountUpProvider>
	{/if}
</FadeContainer>
