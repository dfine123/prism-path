<script lang="ts">
	import { Container } from 'pixi-svelte';

	import RailConsole from './RailConsole.svelte';
	import { getContext } from '../context';
	import type { LayoutUiProps } from '../types';

	// Mobile landscape shares the compact console (same 1920-wide standard space as
	// desktop): floating bar + breakout hero + stacked auto/turbo, buy detached left.
	const props: LayoutUiProps = $props();
	const context = getContext();
</script>

<Container x={20}>
	{@render props.gameName()}
</Container>

<Container x={context.stateLayoutDerived.canvasSizes().width - 20}>
	{@render props.logo()}
</Container>

<RailConsole {...props} />
