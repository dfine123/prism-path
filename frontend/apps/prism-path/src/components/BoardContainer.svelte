<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Container } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { stateFx } from '../game/stateFx.svelte';

	type Props = {
		children: Snippet;
	};

	const props: Props = $props();

	const context = getContext();
</script>

<!-- boardScale/boardNudgeY: shared board-feel channels (spin breath, dragon-slam thud).
     The pivot is the board centre, so the breath expands around the middle and tucks
     under the frame lip; every BoardContainer layer reads the same state = moves as one. -->
<Container
	x={context.stateGameDerived.boardLayout().x}
	y={context.stateGameDerived.boardLayout().y + stateFx.boardNudgeY}
	pivot={context.stateGameDerived.boardLayout().pivot}
	scale={stateFx.boardScale}
>
	{@render props.children()}
</Container>
