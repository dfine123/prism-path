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
		font-size: 1.02rem;
		line-height: 1.16rem;
		letter-spacing: 0.01em;
		text-align: center;
		color: #fff4dc;
		text-shadow: 0 2px 0 rgba(22, 10, 36, 0.85);
	}

	.description {
		font-family: 'Superui', sans-serif;
		font-size: 0.74rem;
		letter-spacing: 0.03em;
		line-height: 1.06rem;
		text-align: center;
		color: #cdbff2;
		// a fixed floor keeps every card's CTA on the same baseline no matter how long the
		// copy is, without stretching short cards
		min-height: 3.18rem;
		white-space: pre-line;
		display: flex;
		align-items: flex-start;
		justify-content: center;
	}

	.description:empty {
		display: none;
	}

	.price {
		font-family: 'Prism', 'Superui', sans-serif;
		font-size: 1.28rem;
		line-height: 1.3rem;
		text-align: center;
		white-space: nowrap;
		color: #ffd25e;
		text-shadow:
			0 2px 0 rgba(22, 10, 36, 0.9),
			0 0 18px rgba(255, 210, 94, 0.28);
	}

	.cta {
		font-family: 'Superui', sans-serif;
		font-weight: 700;
		letter-spacing: 0.16em;
		font-size: 0.84rem;
		color: #12081d;
		text-align: center;
		padding: 0.62rem 0 0.58rem;
		width: 100%;
		clip-path: polygon(
			9px 0,
			calc(100% - 9px) 0,
			100% 9px,
			100% calc(100% - 9px),
			calc(100% - 9px) 100%,
			9px 100%,
			0 calc(100% - 9px),
			0 9px
		);
		background: linear-gradient(180deg, #8fe6ff 0%, #2bb8e8 46%, #1f8fbe 100%);
		box-shadow:
			inset 0 1px 0 rgba(255, 255, 255, 0.6),
			inset 0 -2px 0 rgba(0, 0, 0, 0.22);
		transition: filter 120ms ease;
	}

	.cta:hover {
		filter: brightness(1.1);
	}

	.cta-activate {
		background: linear-gradient(180deg, #ffeaa8 0%, #ffd25e 46%, #dc9f2e 100%);
	}
</style>
