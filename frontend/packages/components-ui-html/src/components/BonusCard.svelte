<script lang="ts">
	import type { Snippet } from 'svelte';

	type Props = {
		image?: string;
		title: Snippet;
		description: Snippet;
		price: Snippet;
		button: Snippet;
	};

	const props: Props = $props();
</script>

<!-- CUT CRYSTAL card: chamfered gem-cut silhouette (clip-path), board-glass surface with a
     top-light sheen, lavender facet border (outer clipped layer = the border colour, inner
     clipped layer = the glass). Mirrors the in-game PrismPanel plaque. -->
<div class="facet">
	<div class="bonus-card-wrap">
		{#if props.image}
			<div class="art">
				<img src={props.image} alt="" draggable="false" />
			</div>
		{/if}
		<div class="info">
			{@render props.title()}
			{@render props.description()}
			{@render props.price()}
		</div>
		{@render props.button()}
	</div>
</div>

<style lang="scss">
	$cut: 14px;

	.facet {
		// the facet border: this layer's background IS the border colour, revealed as a
		// 1.5px rim around the inner glass (both share the chamfered clip)
		clip-path: polygon(
			$cut 0,
			calc(100% - #{$cut}) 0,
			100% $cut,
			100% calc(100% - #{$cut}),
			calc(100% - #{$cut}) 100%,
			$cut 100%,
			0 calc(100% - #{$cut}),
			0 $cut
		);
		background: linear-gradient(180deg, rgba(217, 204, 255, 0.75), rgba(217, 204, 255, 0.35));
		padding: 1.5px;
		min-width: 155px;
		max-width: 190px;
	}

	.bonus-card-wrap {
		padding: 0.6rem;
		flex-direction: column;
		display: flex;
		justify-content: space-between;
		gap: 0.5rem;
		height: 100%;
		text-align: left;

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
		// board glass: deep violet with the top-light sheen falling down the first third
		background:
			linear-gradient(180deg, rgba(191, 168, 255, 0.14), rgba(191, 168, 255, 0) 34%),
			rgba(20, 11, 36, 0.94);
	}

	.art {
		line-height: 0;
		display: flex;
		justify-content: center;
		padding: 0.25rem 0;
	}

	.art img {
		width: auto;
		height: 110px;
		object-fit: contain;
		filter: drop-shadow(0 0 14px rgba(191, 168, 255, 0.35));
	}

	.info {
		display: flex;
		flex-direction: column;
		gap: 0.5em;
	}
</style>
