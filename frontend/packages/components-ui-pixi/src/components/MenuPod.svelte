<script lang="ts">
	import type { Snippet } from 'svelte';

	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import { MainContainer } from 'components-layout';
	import { Container, Rectangle } from 'pixi-svelte';
	import type { ButtonProps } from 'components-pixi';

	import UiGlass from './UiGlass.svelte';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';

	// The menu popup: a vertical glass pod of system controls rising from the menu button.
	// Dim scrim behind it; tapping the scrim closes (state logic unchanged from template).
	type Props = {
		buttonPayTable: Snippet<[Partial<ButtonProps>]>;
		buttonGameRules: Snippet<[Partial<ButtonProps>]>;
		buttonSettings: Snippet<[Partial<ButtonProps>]>;
		buttonSoundSwitch: Snippet<[Partial<ButtonProps>]>;
		buttonMenuClose: Snippet<[Partial<ButtonProps>]>;
		x: number;
		bottomY: number; // pod bottom edge (rises upward from here)
	};

	const props: Props = $props();
	const context = getContext();
	const T = SUPER_UI;

	const step = T.btn + T.gap;
	const podH = step * 5 - T.gap + T.pad * 2;
	const podW = T.btn + T.pad * 2;
</script>

{#if stateUi.menuOpen}
	<Rectangle
		eventMode="static"
		cursor="pointer"
		alpha={0.55}
		anchor={0.5}
		backgroundColor={BLACK}
		width={context.stateLayoutDerived.canvasSizes().width}
		height={context.stateLayoutDerived.canvasSizes().height}
		x={context.stateLayoutDerived.canvasSizes().width * 0.5}
		y={context.stateLayoutDerived.canvasSizes().height * 0.5}
		onpointerup={() => (stateUi.menuOpen = false)}
	/>

	<MainContainer standard alignVertical="bottom">
		<UiGlass x={props.x} y={props.bottomY - podH / 2} width={podW} height={podH} radius={T.railR} tone="panel" />
		{#each [props.buttonPayTable, props.buttonGameRules, props.buttonSettings, props.buttonSoundSwitch, props.buttonMenuClose] as snippet, i (i)}
			<Container x={props.x} y={props.bottomY - T.pad - T.btn / 2 - step * (4 - i)}>
				{@render snippet({ anchor: 0.5 })}
			</Container>
		{/each}
	</MainContainer>
{/if}
