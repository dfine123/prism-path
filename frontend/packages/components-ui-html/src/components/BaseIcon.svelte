<script lang="ts">
	// Chamfered crystal key — the base plate behind every DOM button/option label.
	// Same facet construction as BonusCard/BetMenuAmountToggle: a rim layer whose
	// background IS the edge light, revealed ~1.5px around the plum-glass face.
	type Props = {
		width: string;
		height: string;
		selected?: boolean;
		disabled?: boolean;
	};

	const { width, height, selected = false, disabled = false }: Props = $props();
</script>

<span
	class="facet"
	class:selected
	class:disabled
	style="--width-value: {width}; --height-value: {height};"
>
	<span class="face"></span>
</span>

<style lang="scss">
	$cut: 10px;
	$inner: 9px;

	.facet {
		display: block;
		width: var(--width-value);
		height: var(--height-value);
		box-sizing: border-box;
		padding: 1.5px;
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
		background: linear-gradient(180deg, rgba(217, 204, 255, 0.55), rgba(217, 204, 255, 0.2));
		transition:
			background 120ms ease,
			filter 120ms ease,
			transform 120ms ease;
	}

	.face {
		display: block;
		width: 100%;
		height: 100%;
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
		// plum glass with the top-light sheen falling across the upper half
		background:
			linear-gradient(180deg, rgba(191, 233, 255, 0.18), rgba(191, 233, 255, 0) 52%),
			linear-gradient(180deg, rgba(72, 56, 106, 0.96), rgba(30, 20, 50, 0.96));
		transition:
			background 120ms ease,
			filter 120ms ease;
	}

	// hover = lit rim (the wrapping shared Button is the hover surface, because the
	// absolutely-positioned label overlay sits above this plate)
	:global(button:not(:disabled):hover) > .facet {
		background: linear-gradient(180deg, rgba(191, 233, 255, 0.9), rgba(191, 233, 255, 0.4));
	}

	:global(button:not(:disabled):hover) > .facet .face {
		filter: brightness(1.15);
	}

	// pressed = slight scale-down
	:global(button:not(:disabled):active) > .facet {
		transform: scale(0.96);
	}

	// selected = gold ring + brighter face (drop-shadow, not box-shadow: the clip-path
	// would cut a box-shadow off, while filter applies to the clipped silhouette)
	.facet.selected {
		background: linear-gradient(180deg, #ffeaa8 0%, #ffd25e 46%, #dc9f2e 100%);
		filter: drop-shadow(0 0 6px rgba(255, 210, 94, 0.45));
	}

	.facet.selected .face {
		background:
			linear-gradient(180deg, rgba(255, 234, 168, 0.24), rgba(255, 234, 168, 0) 55%),
			linear-gradient(180deg, rgba(96, 76, 138, 0.98), rgba(44, 30, 72, 0.98));
	}

	.facet.disabled {
		opacity: 0.42;
	}
</style>
