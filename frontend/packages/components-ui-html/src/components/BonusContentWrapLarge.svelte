<script lang="ts">
	import type { Snippet } from 'svelte';

	import BaseContent from './BaseContent.svelte';
	import BaseScrollable from './BaseScrollable.svelte';

	type Props = {
		betAmount: Snippet;
		bonusCardsActivate: Snippet;
		bonusCardsBuy: Snippet;
	};

	const props: Props = $props();
</script>

<BaseContent maxWidth="100%">
	{@render props.betAmount()}

	<BaseScrollable type="column">
		<div class="bonuses-wrap">
			{@render props.bonusCardsActivate()}
			{@render props.bonusCardsBuy()}
		</div>
	</BaseScrollable>
</BaseContent>

<style lang="scss">
	.bonuses-wrap {
		display: flex;
		flex-direction: row;
		// real air between cards, and room for the hover lift so nothing clips
		gap: 1.4rem;
		flex-wrap: wrap;
		justify-content: center;
		align-items: stretch;
		padding: 0.5rem 0.25rem 1rem;
	}
</style>
