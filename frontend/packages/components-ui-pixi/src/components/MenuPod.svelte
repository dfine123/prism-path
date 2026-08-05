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

	// open/close MOTION (was a single-frame hard cut — audit HIGH): the scrim fades
	// and the pod rises from the menu button with a settle; both collapse on close.
	// The pod stays mounted through the exit so the animation can play.
	let anim = $state(stateUi.menuOpen ? 1 : 0);
	let raf = 0;
	$effect(() => {
		const target = stateUi.menuOpen ? 1 : 0;
		cancelAnimationFrame(raf);
		const from = anim;
		if (Math.abs(target - from) < 0.001) return;
		const start = performance.now();
		const ms = stateUi.menuOpen ? 200 : 150;
		const frame = () => {
			const u = Math.min(1, (performance.now() - start) / ms);
			const e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
			anim = from + (target - from) * e;
			if (u < 1) raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});
	// settle overshoot on the pod rise only (never on the scrim)
	const podRise = $derived((1 - anim) * 46);
</script>

{#if stateUi.menuOpen || anim > 0.001}
	<Rectangle
		eventMode={stateUi.menuOpen ? 'static' : 'none'}
		cursor="pointer"
		alpha={0.55 * anim}
		anchor={0.5}
		backgroundColor={BLACK}
		width={context.stateLayoutDerived.canvasSizes().width}
		height={context.stateLayoutDerived.canvasSizes().height}
		x={context.stateLayoutDerived.canvasSizes().width * 0.5}
		y={context.stateLayoutDerived.canvasSizes().height * 0.5}
		onpointerup={() => (stateUi.menuOpen = false)}
	/>

	<MainContainer standard alignVertical="bottom">
		<Container y={podRise} alpha={anim}>
			<UiGlass x={props.x} y={props.bottomY - podH / 2} width={podW} height={podH} radius={T.railR} tone="panel" />
			{#each [props.buttonPayTable, props.buttonGameRules, props.buttonSettings, props.buttonSoundSwitch, props.buttonMenuClose] as snippet, i (i)}
				<Container x={props.x} y={props.bottomY - T.pad - T.btn / 2 - step * (4 - i)}>
					{@render snippet({ anchor: 0.5 })}
				</Container>
			{/each}
		</Container>
	</MainContainer>
{/if}
