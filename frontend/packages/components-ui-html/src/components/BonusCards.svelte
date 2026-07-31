<script lang="ts">
	import { stateBet, stateModal, type BetModeData } from 'state-shared';
	import { Button } from 'components-shared';
	import { getContextEventEmitter } from 'utils-event-emitter';
	import { numberToCurrencyString } from 'utils-shared/amount';

	import BonusCard from './BonusCard.svelte';
	import { stateBonus } from '../stateBonus.svelte';
	import type { EmitterEventModal } from '../types';

	type Props = {
		list: BetModeData[];
	};

	const props: Props = $props();
	const { eventEmitter } = getContextEventEmitter<EmitterEventModal>();
</script>

{#each props.list as betModeData}
	{#if betModeData.type !== 'default'}
		<BonusCard image={betModeData.assets?.dialogImage}>
			{#snippet title()}
				<div class="title">
					{betModeData.text.title}
				</div>
			{/snippet}

			{#snippet description()}
				{#if betModeData?.text?.description}
					<div class="description">
						{betModeData.text.description}
					</div>
				{/if}
			{/snippet}

			{#snippet price()}
				<div class="price">
					{`${numberToCurrencyString(stateBet.betAmount * betModeData.costMultiplier)}`}
				</div>
			{/snippet}

			{#snippet button()}
				<Button
					onclick={() => {
						stateBonus.selectedBetModeKey = betModeData.mode;
						eventEmitter.broadcast({ type: 'buyBonusConfirm' });
						eventEmitter.broadcast({ type: 'soundPressGeneral' });
					}}
					disabled={stateBet.betAmount <= 0 ||
						stateBet.balanceAmount < stateBet.betAmount * betModeData.costMultiplier}
				>
					<!-- crystal CTA: ACTIVATE = gold, BUY = prism cyan->teal (chamfered like
					     the cards; disabled state comes from Button's own opacity) -->
					<div class="cta" class:cta-activate={betModeData.type === 'activate'}>
						{betModeData.text.button}
					</div>
				</Button>
			{/snippet}
		</BonusCard>
	{/if}
{/each}

<style lang="scss">
	// type hierarchy mirrors the game: Prism (Chango) = display, Superui (Fredoka) = voice
	.title {
		font-family: 'Prism', 'Superui', sans-serif;
		font-size: 1rem;
		line-height: 1.15rem;
		text-align: center;
		color: #fff4dc;
		text-shadow: 0 2px 0 rgba(22, 10, 36, 0.8);
	}

	.description {
		font-family: 'Superui', sans-serif;
		font-size: 0.72rem;
		letter-spacing: 0.04em;
		line-height: 1.05rem;
		text-align: center;
		color: #d9ccff;
		min-height: 3.2rem;
		white-space: pre-line;
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}

	.description:empty {
		display: none;
	}

	.price {
		font-family: 'Prism', 'Superui', sans-serif;
		font-size: 1.05rem;
		line-height: 1.1rem;
		text-align: center;
		white-space: nowrap;
		color: #ffd25e;
		text-shadow: 0 2px 0 rgba(22, 10, 36, 0.8);
	}

	.cta {
		font-family: 'Superui', sans-serif;
		font-weight: 600;
		letter-spacing: 0.14em;
		font-size: 0.9rem;
		color: #160a24;
		text-align: center;
		padding: 0.55rem 0;
		width: 100%;
		clip-path: polygon(
			8px 0,
			calc(100% - 8px) 0,
			100% 8px,
			100% calc(100% - 8px),
			calc(100% - 8px) 100%,
			8px 100%,
			0 calc(100% - 8px),
			0 8px
		);
		background: linear-gradient(180deg, #7de0ff, #2bb8e8 45%, #34c0a1);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
	}

	.cta-activate {
		background: linear-gradient(180deg, #ffe9a8, #ffd25e 45%, #e6a83a);
	}
</style>
