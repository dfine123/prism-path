<script lang="ts">
	import { stateBet, stateBetDerived, stateConfig } from 'state-shared';
	import { Button, OptionsToggle } from 'components-shared';
	import { getContextEventEmitter } from 'utils-event-emitter';
	import { numberToCurrencyString } from 'utils-shared/amount';

	import type { EmitterEventModal } from '../types';

	const { eventEmitter } = getContextEventEmitter<EmitterEventModal>();

</script>

<OptionsToggle
	value={stateBet.betAmount}
	options={stateConfig.betAmountOptions}
	onchange={(value) => {
		// same affordability clamp as the +/- steppers — a direct assignment let the menu
		// select a bet the balance cannot cover (and skipped the bet-level snap)
		stateBetDerived.setBetAmount(value);
		eventEmitter.broadcast({ type: 'soundPressGeneral' });
	}}
>
	{#snippet children({ disabledDown, disabledUp, toggleDown, toggleUp })}
		<div class="toggle-wrap">
			<span class="caption">BET</span>

			<Button data-test="down-button" disabled={disabledDown} onclick={toggleDown}>
				<span class="step">&minus;</span>
			</Button>

			<span class="amount">{numberToCurrencyString(stateBet.betAmount)}</span>

			<Button data-test="up-button" disabled={disabledUp} onclick={toggleUp}>
				<span class="step">+</span>
			</Button>
		</div>
	{/snippet}
</OptionsToggle>

<style lang="scss">
	// the bet selector is part of the same crystal console language as the cards below it:
	// chamfered glass keys either side of a recessed readout well
	.toggle-wrap {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 0.6rem;
		padding: 0.5rem 0.9rem;
		background:
			linear-gradient(180deg, rgba(191, 168, 255, 0.12), rgba(191, 168, 255, 0) 60%),
			rgba(20, 11, 36, 0.9);
		border: 1.5px solid rgba(217, 204, 255, 0.4);
		clip-path: polygon(
			13px 0,
			calc(100% - 13px) 0,
			100% 13px,
			100% calc(100% - 13px),
			calc(100% - 13px) 100%,
			13px 100%,
			0 calc(100% - 13px),
			0 13px
		);
	}

	.caption {
		font-family: 'Superui', sans-serif;
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.2em;
		color: #a79cc4;
		padding-right: 0.15rem;
	}

	.step {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.1rem;
		height: 2.1rem;
		font-family: 'Superui', sans-serif;
		font-size: 1.35rem;
		font-weight: 700;
		line-height: 1;
		color: #fff4dc;
		background: linear-gradient(180deg, rgba(72, 56, 106, 0.95), rgba(38, 26, 62, 0.95));
		border: 1.5px solid rgba(217, 204, 255, 0.35);
		border-radius: 9px;
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22);
		transition: filter 120ms ease;
	}

	.step:hover {
		filter: brightness(1.25);
	}

	.amount {
		font-family: 'Prism', 'Superui', sans-serif;
		font-size: 1.1rem;
		line-height: 1;
		color: #fff4dc;
		text-shadow: 0 2px 0 rgba(22, 10, 36, 0.85);
		min-width: 6.2rem;
		text-align: center;
		padding: 0.42rem 0.5rem;
		background: rgba(8, 4, 15, 0.55);
		border-radius: 8px;
		box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.5);
	}
</style>
