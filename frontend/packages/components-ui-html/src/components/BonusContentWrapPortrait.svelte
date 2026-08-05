<script lang="ts">
	import type { Snippet } from 'svelte';

	import BaseContent from './BaseContent.svelte';
	import BaseScrollable from './BaseScrollable.svelte';

	type Props = {
		maxListLength: number; // kept for call-site parity with the landscape/desktop wraps
		betAmount: Snippet;
		bonusCardsActivate: Snippet;
		bonusCardsBuy: Snippet;
	};

	const props: Props = $props();
</script>

<!-- Portrait: NO scale-to-fit (0.41x with 4 cards was illegible on phones — audit).
     The cards flow as a 2-up grid inside a real scroll area, full legible size, with
     the bet stepper pinned below the scroll. Landscape/desktop keep their own wraps. -->
<BaseContent maxWidth="100%">
	<div class="portrait-wrap">
		<BaseScrollable type="column">
			<div class="cards">
				{@render props.bonusCardsActivate()}
				{@render props.bonusCardsBuy()}
			</div>
		</BaseScrollable>

		<div class="bet-wrap">
			{@render props.betAmount()}
		</div>
	</div>
</BaseContent>

<style lang="scss">
	.portrait-wrap {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.9rem;
		width: min(94vw, 430px);
		// bounded height so the card grid scrolls INSIDE the modal (close key above,
		// bet stepper below stay reachable)
		max-height: calc(100dvh - 7.5rem);
	}

	// the BaseScrollable column is the flexible track; min-height lets it shrink
	.portrait-wrap > :global(.content.column) {
		flex: 1 1 auto;
		min-height: 0;
		width: 100%;
	}

	.cards {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.75rem;
		width: 100%;
		box-sizing: border-box;
		// side inset keeps the hover-lift and facet edges clear of the scroll clip
		padding: 0.25rem 0.25rem 0.5rem;
	}

	// BonusCard fixes itself at 232px for the landscape/desktop rows; in portrait each
	// card stretches to its grid track instead (.facet is BonusCard's root plate)
	.cards > :global(.facet) {
		width: 100%;
	}

	// BUY/ACTIVATE must stay a real thumb target on phones (>= 44px at 390px width)
	.cards :global(.cta) {
		min-height: 44px;
		box-sizing: border-box;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.4rem 0;
	}

	.bet-wrap {
		flex: 0 0 auto;
	}
</style>
