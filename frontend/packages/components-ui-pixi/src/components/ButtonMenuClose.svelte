<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateUi } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const sizes = { width: SUPER_UI.btn, height: SUPER_UI.btn };

	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateUi.menuOpen = false;
	};
</script>

<UiButton {...props} {sizes} {onpress} icon="menuExit" />
