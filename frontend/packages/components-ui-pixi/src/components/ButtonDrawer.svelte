<script lang="ts">
	// Portrait drawer toggle — Crystal Console control (was the template's last raw
	// placeholder: black UiSprite stub + a fallback-font '↓'). Glass face, drawn
	// chevron that rotates with the fold, standard press/disabled states, press sound.
	import { cubicInOut } from 'svelte/easing';
	import { Tween } from 'svelte/motion';

	import { stateUi } from 'state-shared';
	import { Container, Graphics } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';

	import UiGlass from './UiGlass.svelte';
	import { drawGlyph } from '../glyphs';
	import { SUPER_UI } from '../theme';
	import { getContext } from '../context';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const T = SUPER_UI;
	const sizes = { width: T.btnSm, height: T.btnSm };

	const DRAWER_ROTATION = {
		up: -Math.PI,
		down: 0,
	};

	const rotationTween = new Tween(stateUi.drawerFold ? DRAWER_ROTATION.up : DRAWER_ROTATION.down, {
		easing: cubicInOut,
	});

	let moving = $state(false);
	const disabled = $derived(props.disabled || moving);

	const onpress = async () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		if (stateUi.drawerFold) {
			await context.eventEmitter.broadcastAsync({ type: 'drawerUnfold' });
		} else {
			await context.eventEmitter.broadcastAsync({ type: 'drawerFold' });
		}
	};

	context.eventEmitter.subscribeOnMount({
		drawerUnfold: async () => {
			if (stateUi.drawerFold) {
				moving = true;
				await rotationTween.set(DRAWER_ROTATION.down);
				stateUi.drawerFold = false;
				moving = false;
			}
		},
		drawerFold: async () => {
			if (!stateUi.drawerFold) {
				moving = true;
				await rotationTween.set(DRAWER_ROTATION.up);
				stateUi.drawerFold = true;
				moving = false;
			}
		},
	});
</script>

<Button {...props} {sizes} {onpress} {disabled}>
	{#snippet children({ center, hovered, pressed })}
		<Container {...center} scale={pressed ? T.press : 1} alpha={disabled ? T.dim : 1}>
			<UiGlass
				width={T.btnSm}
				height={T.btnSm}
				radius={T.btnSm / 2}
				lit={!disabled && hovered}
			/>
			<Container rotation={rotationTween.current}>
				<Graphics
					draw={(g) => {
						g.clear();
						drawGlyph(g, { icon: 'chevronDown', size: T.btnSm * 0.52, color: T.color.text });
					}}
				/>
			</Container>
		</Container>
	{/snippet}
</Button>
