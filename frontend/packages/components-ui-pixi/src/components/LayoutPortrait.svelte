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

	// Portrait "Crystal Console" v2 — reference-informed two-row stack (operator
	// direction, 2026-08-04):
	//   ROW 1 (action):  BUY | [-]  BET  [+] | HERO | auto/turbo stacked
	//   ROW 2 (money):   MENU | BALANCE wide | WIN
	// One visual hierarchy, generous tap targets, no floating strays. The DRAWER
	// mechanics stay: row 1 + menu/balance fold away during free spins; the WIN
	// capsule holds its ground and the FS counter takes the balance slot.
	const props: LayoutUiProps = $props();
	const context = getContext();
	const T = SUPER_UI;

	// row geometry (standard portrait space: 1080 x 1920)
	const ROW1_Y = 330; // from bottom
	const ROW2_Y = 128;
	const X_EDGE = 110; // buy / menu column
	const X_STEP_DEC = 268;
	const X_BET = 400;
	const X_STEP_INC = 532;
	const X_HERO = 770;
	const X_STACK = 985; // auto/turbo + drawer button column
	const X_BALANCE = 430;
	const X_WIN = 830;
	const STEP_SIZE = { width: 104, height: 104 };
	const HERO_SIZE = { width: 224, height: 224 };

	const DRAWER_Y = {
		unfold: 0,
		fold: 550,
	};
	const drawerTween = new Tween(stateUi.drawerFold ? DRAWER_Y.fold : DRAWER_Y.unfold, {
		easing: cubicInOut,
	});

	const DRAWER_BUTTON_Y = {
		unfold: 0,
		// keep the folded toggle FULLY on-screen and clear of the iOS home-indicator
		// swipe zone (the old 50 buried half the button off the bottom edge)
		fold: 14,
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

	const H = $derived(context.stateLayoutDerived.mainLayoutStandard().height);
</script>

<Container x={20}>
	{@render props.gameName()}
</Container>

<Container x={context.stateLayoutDerived.canvasSizes().width - 20}>
	{@render props.logo()}
</Container>

<MainContainer standard alignVertical="bottom">
	<!-- drawer group: row 1 + menu/balance (folds away during free spins) -->
	<Container y={drawerTween.current}>
		<!-- ROW 1: buy | [-] bet [+] | hero | auto/turbo stack. The steppers overlap the
		     capsule's end caps ON TOP (reference look) — they render after it. -->
		<Container x={X_EDGE} y={H - ROW1_Y}>{@render props.buttonBuyBonus({ anchor: 0.5 })}</Container>
		<Container x={X_BET} y={H - ROW1_Y}>
			{@render props.amountBet({ stacked: true, width: 236 })}
		</Container>
		<Container x={X_STEP_DEC} y={H - ROW1_Y}>{@render props.buttonDecrease({ anchor: 0.5, sizes: STEP_SIZE })}</Container>
		<Container x={X_STEP_INC} y={H - ROW1_Y}>{@render props.buttonIncrease({ anchor: 0.5, sizes: STEP_SIZE })}</Container>
		<Container x={X_HERO} y={H - ROW1_Y}>{@render props.buttonBet({ anchor: 0.5, sizes: HERO_SIZE })}</Container>
		<Container x={X_STACK} y={H - ROW1_Y - 66}>{@render props.buttonAutoSpin({ anchor: 0.5, labelScale: 1.25 })}</Container>
		<Container x={X_STACK} y={H - ROW1_Y + 66}>{@render props.buttonTurbo({ anchor: 0.5, labelScale: 1.25 })}</Container>

		<!-- ROW 2: menu | balance (menu gets a full-size face: 92std was a ~33pt
		     phone tap target, under the 44pt floor) -->
		<Container x={X_EDGE} y={H - ROW2_Y}>{@render props.buttonMenu({ anchor: 0.5, sizes: { width: 118, height: 118 }, labelScale: 1.25 })}</Container>
		<Container x={X_BALANCE} y={H - ROW2_Y}>
			{@render props.amountBalance({ stacked: true, width: 470 })}
		</Container>
	</Container>

	<!-- WIN capsule holds its ground through the drawer fold (free spins keep it) -->
	<Container x={X_WIN} y={H - ROW2_Y}>
		{@render props.amountWin({ stacked: true, width: 290 })}
	</Container>

	<!-- free spins: once the drawer has vacated the row, the counter takes the
	     balance slot and a compact BALANCE stays on screen (stake/balance visibility
	     during play). Gated on drawerFold so nothing stamps over the real balance
	     during the fold beat — or after a manual unfold. -->
	{#if stateUi.freeSpinCounterShow && stateUi.drawerFold}
		<Container x={150} y={H - ROW2_Y}>
			{@render props.amountBalance({ stacked: true, width: 250 })}
		</Container>
		<Container x={X_BALANCE + 45} y={H - ROW2_Y}>
			<LabelFreeSpinCounter stacked />
		</Container>
	{/if}

	<!-- drawer button: bottom-right, clear of the win capsule -->
	<FadeContainer
		persistent
		show={stateUi.drawerButtonShow}
		oncomplete={drawerButtonFadeComplete}
		y={drawerButtonTween.current}
	>
		<Container x={X_STACK} y={H - ROW2_Y}>
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
	x={X_EDGE}
	bottomY={H - ROW1_Y - 110}
/>
