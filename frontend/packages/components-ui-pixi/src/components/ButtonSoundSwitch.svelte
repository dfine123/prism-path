<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateSound } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { SUPER_UI } from '../theme';
	import { getContext } from '../context';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const sizes = { width: SUPER_UI.btn, height: SUPER_UI.btn };

	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });

		if (stateSound.volumeValueMaster === 0) {
			stateSound.volumeValueMaster = 50;
		} else {
			stateSound.volumeValueMaster = 0;
		}
	};

	const icon = $derived(
		stateSound.volumeValueMaster === 0 ? ('soundOff' as const) : ('soundOn' as const),
	);
</script>

<UiButton {...props} {sizes} {onpress} {icon} variant="light" />
