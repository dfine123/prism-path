<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateSound, stateSoundHandler } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { SUPER_UI } from '../theme';
	import { getContext } from '../context';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const sizes = { width: SUPER_UI.btn, height: SUPER_UI.btn };

	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });

		// mute remembers the user's level; unmute restores it (shared with the DOM
		// settings sliders, so both controls agree on the restore point)
		stateSoundHandler.toggleVolumeValue('volumeValueMaster');
	};

	const icon = $derived(
		stateSound.volumeValueMaster === 0 ? ('soundOff' as const) : ('soundOn' as const),
	);
</script>

<UiButton {...props} {sizes} {onpress} {icon} variant="light" />
