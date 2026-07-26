<script lang="ts">
	import { Container } from 'pixi-svelte';

	import RailConsole from './RailConsole.svelte';
	import { getContext } from '../context';
	import type { LayoutUiProps } from '../types';

	// Tablet = the standard rail + the free-spin counter perched above it.
	const props: LayoutUiProps = $props();
	const context = getContext();
</script>

<Container x={20}>
	{@render props.gameName()}
</Container>

<Container x={context.stateLayoutDerived.canvasSizes().width - 20}>
	{@render props.logo()}
</Container>

<RailConsole {...props} fsCounter />
