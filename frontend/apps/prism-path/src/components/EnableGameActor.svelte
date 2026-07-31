<script lang="ts">
	import { onMount } from 'svelte';

	import { Text } from 'pixi-svelte';

	import { gameActor } from '../game/actor';
	import { getContext } from '../game/context';
	import { isBookPlaying } from '../game/utils';

	type Props = {
		debug?: boolean;
	};

	const props: Props = $props();
	const context = getContext();

	onMount(() => {
		const { unsubscribe } = gameActor.subscribe((snapshot) => {
			context.stateXstate.value = snapshot.value;
			// const childActor = snapshot.children[snapshot.value];
		});

		gameActor.start();
		gameActor.send({ type: 'RENDERED' });

		return () => {
			// Equivalent to onDestroy(); Leave this comment for searching.
			unsubscribe();
			gameActor.stop();
		};
	});

	context.eventEmitter.subscribeOnMount({
		// Connect every actor with app.eventEmitter to avoid call actor directly.
		// BET/AUTO_BET are refused while ANY book is already presenting — the machine can
		// sit in idle during storybook Action-driven playback, and accepting a wager there
		// started a second, concurrent round over the live one.
		bet: () => {
			if (!isBookPlaying()) gameActor.send({ type: 'BET' });
		},
		autoBet: () => {
			if (!isBookPlaying()) gameActor.send({ type: 'AUTO_BET' });
		},
		resumeBet: () => gameActor.send({ type: 'RESUME_BET' }),
	});
</script>

{#if props.debug}
	<Text
		x={context.stateLayoutDerived.canvasSizes().width}
		anchor={{ x: 1, y: 0 }}
		style={{ fill: 0xffffff }}
		text={JSON.stringify(context.stateXstate.value, undefined, 2)}
	/>
{/if}
