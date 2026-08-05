<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateUi } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { SUPER_UI } from '../theme';
	import { getContext } from '../context';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const sizes = $derived(props.sizes ?? { width: SUPER_UI.btnSm, height: SUPER_UI.btnSm });

	const onpress = () => {
		// a win presentation owns the stage: a press there means CONTINUE, never "open
		// the system menu on top of the celebration"
		if (stateUi.pressCatcherActive) return;
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateUi.menuOpen = true;
	};
</script>

<UiButton {...props} {sizes} {onpress} icon="menu" />
