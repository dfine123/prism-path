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
						// GENERATION GUARD: capture the resolve this timer belongs to — a
						// press-skip can retire this presentation and arm the NEXT one before
						// the timeout fires; a stale timer must never resolve the new await
						const myResolve = oncomplete;
						await startCountUp();
						// an instant amount needs a longer static hold than a rolled one — the
						// roll itself was the reading time
						await waitForTimeout(rollsUp ? 300 : 650);
						if (oncomplete === myResolve) oncomplete();
					}}
				/>

			<!-- shards render UNDER the box — gems erupt from behind the plaque, never
				     over the text -->
				{#if isBigWin}
					<PrismShards emit={!countUpCompleted} levelAlias={winLevelData?.alias} />
				{/if}

				<MainContainer>
					<Container
						x={context.stateGameDerived.boardLayout().x}
						y={context.stateGameDerived.boardLayout().y}
					>
						{#if isBigWin && winLevelData.text}
							<!-- amount = the LIVE roll: the box promotes itself (word, accent, crest,
							     stinger) as the count-up crosses tier bands, clamped to the final level -->
							<WinBox level={winLevelData.level} amount={countUpAmount}>
								<ResponsiveBitmapText
									anchor={0.5}
									maxWidth={SYMBOL_SIZE * 4.6}
									text={bookEventAmountToCurrencyString(countUpAmount)}
									style={prismStyle(SYMBOL_SIZE * 1.3, { align: 'center', letterSpacing: 0 })}
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

				<!-- non-box (quick) wins stay light: no shard garnish — the burst is part of the
				     box design and its behind-the-plaque birth would be visible without one -->

				<PressToContinue onpress={() => (countUpCompleted ? oncomplete() : finishCountUp())} />
			{/snippet}
		</WinCountUpProvider>
	{/if}
</FadeContainer>
