<script lang="ts" module>
	// onCovered fires at FULL COVER — the moment to swap what's behind the curtain
	// (background/game state) so the reveal already shows the new scene.
	export type EmitterEventTransition = { type: 'transition'; onCovered?: () => void };
</script>

<script lang="ts">
	import { waitForResolve } from 'utils-shared/wait';

	import TransitionAnimation from './TransitionAnimation.svelte';
	import { getContext } from '../game/context';

	const context = getContext();

	let transitioning = $state(false);
	let oncomplete = $state(() => {});
	let oncovered = $state<(() => void) | undefined>(undefined);

	context.eventEmitter.subscribeOnMount({
		transition: async (emitterEvent) => {
			oncovered = emitterEvent.onCovered;
			transitioning = true;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

{#if transitioning}
	<TransitionAnimation
		oncovered={() => oncovered?.()}
		oncomplete={() => {
			oncomplete();
			transitioning = false;
		}}
	/>
{/if}
