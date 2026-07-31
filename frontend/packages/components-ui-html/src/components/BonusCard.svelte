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

<!-- CUT CRYSTAL feature card: full-bleed key art on top, text block below, CTA at the foot.
     The chamfered silhouette lives on the OUTER frame only; the inner column is a plain
     rect with its own padding, so the CTA can never be sliced by the corner cut (the
     previous build clipped the button because it sat inside the chamfered layer). -->
<div class="facet">
	<div class="card">
		{#if props.image}
			<div class="art">
				<img src={props.image} alt="" draggable="false" />
				<div class="art-fade"></div>
			</div>
		{/if}
		<div class="body">
			<div class="info">
				{@render props.title()}
				{@render props.description()}
			</div>
			<div class="foot">
				{@render props.price()}
				<div class="cta-slot">
					{@render props.button()}
				</div>
			</div>
		</div>
	</div>
</div>

<style lang="scss">
	$cut: 16px;
	$inner: 14.5px;

	.facet {
		// the facet border: this layer's background IS the rim colour, revealed as a ~1.5px
		// edge around the inner card (both share the chamfered clip)
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
		background: linear-gradient(180deg, rgba(217, 204, 255, 0.7), rgba(217, 204, 255, 0.22));
		padding: 1.5px;
		width: 232px;
		flex: 0 0 auto;
		transition: transform 140ms ease;

		&:hover {
			transform: translateY(-3px);
		}
	}

	.card {
		display: flex;
		flex-direction: column;
		height: 100%;
		text-align: center;
		overflow: hidden;

		clip-path: polygon(
			$inner 0,
			calc(100% - #{$inner}) 0,
			100% $inner,
			100% calc(100% - #{$inner}),
			calc(100% - #{$inner}) 100%,
			$inner 100%,
			0 calc(100% - #{$inner}),
			0 $inner
		);
		// board glass, with the top-light sheen falling across the upper third
		background:
			linear-gradient(180deg, rgba(191, 168, 255, 0.13), rgba(191, 168, 255, 0) 38%),
			rgba(20, 11, 36, 0.96);
	}

	// ---- key art: one square window, full bleed to the card's edges ----
	.art {
		position: relative;
		aspect-ratio: 1 / 1;
		overflow: hidden;
		line-height: 0;
		flex: 0 0 auto;
	}

	.art img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		// bias up: every painting puts its subject in the upper-middle
		object-position: 50% 34%;
		display: block;
	}

	// the art dissolves into the card body instead of ending on a hard seam
	.art-fade {
		position: absolute;
		inset: auto 0 -1px 0;
		height: 38%;
		background: linear-gradient(180deg, rgba(20, 11, 36, 0) 0%, rgba(20, 11, 36, 0.92) 78%, rgba(20, 11, 36, 1) 100%);
		pointer-events: none;
	}

	// ---- text + CTA ----
	.body {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		flex: 1 1 auto;
		gap: 0.7rem;
		// generous inset keeps every edge clear of the chamfered corners
		padding: 0.15rem 0.85rem 0.95rem;
	}

	.info {
		display: flex;
		flex-direction: column;
		gap: 0.45rem;
	}

	.foot {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	// the CTA sits fully inside the padding, so the corner cut cannot touch it
	.cta-slot {
		display: block;
	}
</style>
