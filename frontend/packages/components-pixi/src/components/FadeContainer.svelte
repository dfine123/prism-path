<script lang="ts">
	import { onMount } from 'svelte';
	import { Tween } from 'svelte/motion';

	import { Container, type ContainerProps } from 'pixi-svelte';

	type Props = ContainerProps & {
		show: boolean;
		persistent?: boolean;
		duration?: number;
		oncomplete?: () => void;
	};

	const { show, persistent, duration, oncomplete, children, ...restProps }: Props = $props();
	const alpha = new Tween(show ? 1 : 0, { duration: duration });

	$effect(() => {
		alpha.set(show ? 1 : 0, { duration: duration }).then(() => oncomplete?.());
	});

	onMount(async () => {
		if (show) {
			await alpha.set(0, { duration: 0 });
			await alpha.set(1);
			oncomplete?.();
		}
	});
</script>

{#if alpha.current > 0 || persistent}
	<!-- pixi hit-testing ignores alpha: while hidden the subtree must also drop pointer
	     events, or an invisible console keeps clicking under the player's finger -->
	<Container {...restProps} alpha={alpha.current} eventMode={show ? undefined : 'none'}>
		{@render children()}
	</Container>
{/if}
