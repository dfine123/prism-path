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

<style lang="scss">
	.bonus-card-wrap {
		padding: 0.5rem;
		flex-direction: column;
		display: flex;
		justify-content: space-between;

		border-radius: 10px;
		background: rgba(0, 0, 0, 0.55);
		border: 1px solid rgba(255, 255, 255, 0.28);
		text-align: left;
		min-width: 155px;
		max-width: 190px;
		gap: 0.5rem;
	}

	.art {
		border-radius: 8px;
		overflow: hidden;
		line-height: 0;
	}

	.art img {
		width: 100%;
		height: 130px;
		object-fit: cover;
		object-position: top;
	}

	.info {
		display: flex;
		flex-direction: column;
		gap: 0.5em;
	}
</style>
