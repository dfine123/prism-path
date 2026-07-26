<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicInOut } from 'svelte/easing';

	import { stateUi } from 'state-shared';
	import { FadeContainer } from 'components-pixi';
	import { MainContainer } from 'components-layout';
	import { Container } from 'pixi-svelte';
	import { waitForResolve } from 'utils-shared/wait';

	import LabelFreeSpinCounter from './LabelFreeSpinCounter.svelte';
	import ButtonDrawer from './ButtonDrawer.svelte';
	import MenuPod from './MenuPod.svelte';
	import type { LayoutUiProps } from '../types';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';

	// Portrait: the HERO lives dead-centre in the thumb zone with turbo/auto orbiting it
	// and menu/buy at the corners; money capsules stack above. The DRAWER mechanics are
	// the template's proven system, untouched: the action cluster + balance fold away
	// during free spins, leaving win + bet (or the FS counter) on screen.
	const props: LayoutUiProps = $props();
	const context = getContext();
	const T = SUPER_UI;

	const DRAWER_Y = {
		unfold: 0,
		fold: 550,
	};
	const drawerTween = new Tween(stateUi.drawerFold ? DRAWER_Y.fold : DRAWER_Y.unfold, {
		easing: cubicInOut,
	});

	const DRAWER_BUTTON_Y = {
		unfold: 0,
		fold: 50,
	};
	const drawerButtonTween = new Tween(
		stateUi.drawerFold ? DRAWER_BUTTON_Y.fold : DRAWER_BUTTON_Y.unfold,
		{
			easing: cubicInOut,
		},
	);

	let drawerButtonFadeComplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		drawerButtonShow: async () => {
			if (!stateUi.drawerButtonShow) {
				stateUi.drawerButtonShow = true;
				await waitForResolve((resolve) => (drawerButtonFadeComplete = resolve));
			}
		},
		drawerButtonHide: async () => {
			if (stateUi.drawerButtonShow) {
				stateUi.drawerButtonShow = false;
				await waitForResolve((resolve) => (drawerButtonFadeComplete = resolve));
			}
		},
		drawerUnfold: async () => {
			if (stateUi.drawerFold) {
				drawerButtonTween.set(DRAWER_BUTTON_Y.unfold);
				await drawerTween.set(DRAWER_Y.unfold);
			}
		},
		drawerFold: async () => {
			if (!stateUi.drawerFold) {
				drawerButtonTween.set(DRAWER_BUTTON_Y.fold);
				await drawerTween.set(DRAWER_Y.fold);
			}
		},
	});

	const midX = $derived(context.stateLayoutDerived.mainLayoutStandard().width * 0.5);
	const H = $derived(context.stateLayoutDerived.mainLayoutStandard().height);
</script>

<Container x={20}>
	{@render props.gameName()}
</Container>

<Container x={context.stateLayoutDerived.canvasSizes().width - 20}>
	{@render props.logo()}
</Container>

<MainContainer standard alignVertical="bottom">
	<!-- drawer group: action cluster + balance (folds away during free spins) -->
	<Container y={drawerTween.current}>
		<Container x={midX} y={H - 400}>{@render props.buttonBet({ anchor: 0.5 })}</Container>
		<Container x={midX - 195} y={H - 400}>{@render props.buttonAutoSpin({ anchor: 0.5 })}</Container>
		<Container x={midX + 195} y={H - 400}>{@render props.buttonTurbo({ anchor: 0.5 })}</Container>
		<Container x={midX - 440} y={H - 400}>{@render props.buttonMenu({ anchor: 0.5 })}</Container>
		<Container x={midX + 440} y={H - 400}>{@render props.buttonBuyBonus({ anchor: 0.5 })}</Container>

		<Container x={midX} y={H - 234}>
			{@render props.amountBalance({ stacked: true })}
		</Container>
	</Container>

	<!-- win capsule: rides the drawer only until it clears its resting spot -->
	<Container y={Math.min(drawerTween.current, 350)}>
		<Container x={midX} y={H - 634}>
			{@render props.amountWin({ stacked: true })}
		</Container>
	</Container>
</MainContainer>

<MainContainer standard alignVertical="bottom">
	{#if stateUi.freeSpinCounterShow}
		<Container x={midX} y={H - 94}>
			<LabelFreeSpinCounter stacked />
		</Container>
	{:else}
		<Container x={midX} y={H - 94}>
			{@render props.amountBet({ stacked: true })}
		</Container>

		<Container x={midX - 250} y={H - 85}>{@render props.buttonDecrease({ anchor: 0.5 })}</Container>
		<Container x={midX + 250} y={H - 85}>{@render props.buttonIncrease({ anchor: 0.5 })}</Container>
	{/if}

	<!-- drawer button -->
	<FadeContainer
		persistent
		show={stateUi.drawerButtonShow}
		oncomplete={drawerButtonFadeComplete}
		y={drawerButtonTween.current}
	>
		<Container x={midX + 440} y={H - 105}>
			<ButtonDrawer disabled={!stateUi.drawerButtonShow} anchor={0.5} />
		</Container>
	</FadeContainer>
</MainContainer>

<MenuPod
	buttonPayTable={props.buttonPayTable}
	buttonGameRules={props.buttonGameRules}
	buttonSettings={props.buttonSettings}
	buttonSoundSwitch={props.buttonSoundSwitch}
	buttonMenuClose={props.buttonMenuClose}
	x={midX - 440}
	bottomY={H - 480}
/>
