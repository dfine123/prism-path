<script lang="ts">
	import { stateUi } from 'state-shared';
	import { MainContainer } from 'components-layout';
	import { Container, Graphics } from 'pixi-svelte';

	import UiGlass from './UiGlass.svelte';
	import LabelFreeSpinCounter from './LabelFreeSpinCounter.svelte';
	import MenuPod from './MenuPod.svelte';
	import type { LayoutUiProps } from '../types';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';

	// THE UNIFIED CONSOLE DECK (desktop / tablet / landscape): one glass bar, one unit,
	// the hero anchoring its right end cap — the BUY-BONUS star square stands just LEFT
	// of the deck, detached but ALIGNED (taller than the bar, same midline, one composed
	// row centred together), and auto/turbo ride as ONE stacked column:
	//
	//   [★]  [ ≡ │ BALANCE  WIN  BET ± ] (HER○  [⟳]
	//    buy                                └ end cap  [≫]  stacked, outside
	//
	// A RUNNING CURSOR lays the deck out — overlap is impossible by construction.
	type Props = LayoutUiProps & { fsCounter?: boolean };

	const props: Props = $props();
	const context = getContext();
	const T = SUPER_UI;

	const L = $derived.by(() => {
		const W = context.stateLayoutDerived.mainLayoutStandard().width;
		const H = context.stateLayoutDerived.mainLayoutStandard().height;
		// the HERO is the tallest element — the midline clears its radius, not the bar's
		const midY = H - T.railMargin - T.hero / 2 - 4;

		// deck contents, cursor left -> right (positions relative to the bar's LEFT edge)
		let cx = T.bar.padX;
		const menuX = cx + T.bar.menu / 2;
		cx += T.bar.menu + 26;
		const balX = cx + T.bar.balW / 2;
		cx += T.bar.balW + 22;
		const winX = cx + T.bar.winW / 2;
		cx += T.bar.winW + 22;
		const betX = cx + T.bar.betW / 2;
		cx += T.bar.betW + 10;
		const stepX = cx + T.bar.stepper / 2;
		cx += T.bar.stepper + 16;
		// hero sits ON the end cap: its right edge reaches heroPoke past the bar's edge
		const heroX = cx + T.hero / 2;
		const barW = cx + T.hero - T.bar.heroPoke;

		// the composed row = [buy star] + [deck (+ hero poke)] + [outside auto/turbo stack]
		// — centred together as ONE unit
		const BUY_GAP = 20;
		const STACK_GAP = 18;
		const groupW = T.buy.size + BUY_GAP + barW + T.bar.heroPoke + STACK_GAP + T.bar.toggleStack;
		const groupL = (W - groupW) / 2;
		const buyX = groupL + T.buy.size / 2;
		const barL = groupL + T.buy.size + BUY_GAP;
		const stackX = barL + barW + T.bar.heroPoke + STACK_GAP + T.bar.toggleStack / 2;
		return { W, H, midY, barW, barL, buyX, menuX, balX, winX, betX, stepX, heroX, stackX };
	});
</script>

<MainContainer standard alignVertical="bottom">
	<!-- grounding shadows: the deck and hero sit ON the scene, not in it -->
	<Graphics
		draw={(g) => {
			const sy = L.midY + T.bar.h / 2 + 8;
			g.ellipse(L.barL + L.barW / 2, sy, L.barW * 0.47, 14).fill({ color: 0x060310, alpha: 0.2 });
			g.ellipse(L.barL + L.barW / 2, sy, L.barW * 0.38, 8).fill({ color: 0x060310, alpha: 0.16 });
			g.ellipse(L.barL + L.heroX, L.midY + T.hero / 2 + 7, T.hero * 0.42, 11).fill({ color: 0x060310, alpha: 0.22 });
			g.ellipse(L.buyX, L.midY + T.buy.size / 2 + 7, T.buy.size * 0.44, 9).fill({ color: 0x060310, alpha: 0.2 });
		}}
	/>

	<UiGlass x={L.barL + L.barW / 2} y={L.midY} width={L.barW} height={T.bar.h} radius={T.bar.h / 2} tone="panel" seam />

	<!-- zone articulation: a faint divider tick with a crystal diamond, system│money -->
	<Graphics
		draw={(g) => {
			for (const dx of [L.balX - T.bar.balW / 2 - 13]) {
				const x = L.barL + dx;
				g.moveTo(x, L.midY - T.bar.h * 0.26)
					.lineTo(x, L.midY + T.bar.h * 0.26)
					.stroke({ width: 2, color: 0xffffff, alpha: 0.07, cap: 'round' });
				g.poly([
					{ x, y: L.midY - 5 },
					{ x: x + 3.5, y: L.midY },
					{ x, y: L.midY + 5 },
					{ x: x - 3.5, y: L.midY },
				]).fill({ color: T.color.edge, alpha: 0.55 });
			}
		}}
	/>

	<Container x={L.barL}>
		<Container x={L.menuX} y={L.midY}>
			{@render props.buttonMenu({ anchor: 0.5, sizes: { width: T.bar.menu, height: T.bar.menu }, showLabel: false })}
		</Container>

		<Container x={L.balX} y={L.midY}>{@render props.amountBalance({ bare: true, width: T.bar.balW })}</Container>
		<Container x={L.winX} y={L.midY}>{@render props.amountWin({ bare: true, width: T.bar.winW })}</Container>
		<Container x={L.betX} y={L.midY}>{@render props.amountBet({ bare: true, width: T.bar.betW })}</Container>
		<Container x={L.stepX} y={L.midY - T.bar.stepper / 2 - 3}>
			{@render props.buttonIncrease({ anchor: 0.5, sizes: { width: T.bar.stepper, height: T.bar.stepper } })}
		</Container>
		<Container x={L.stepX} y={L.midY + T.bar.stepper / 2 + 3}>
			{@render props.buttonDecrease({ anchor: 0.5, sizes: { width: T.bar.stepper, height: T.bar.stepper } })}
		</Container>

		<Container x={L.heroX} y={L.midY}>{@render props.buttonBet({ anchor: 0.5 })}</Container>
	</Container>

	<!-- auto/turbo: stacked pair OUTSIDE the deck, right of the hero -->
	<Container x={L.stackX} y={L.midY - T.bar.toggleStack / 2 - 4}>
		{@render props.buttonAutoSpin({ anchor: 0.5, sizes: { width: T.bar.toggleStack, height: T.bar.toggleStack }, showLabel: false })}
	</Container>
	<Container x={L.stackX} y={L.midY + T.bar.toggleStack / 2 + 4}>
		{@render props.buttonTurbo({ anchor: 0.5, sizes: { width: T.bar.toggleStack, height: T.bar.toggleStack }, showLabel: false })}
	</Container>

	<!-- buy bonus: the star square — detached from the deck but aligned with it -->
	<Container x={L.buyX} y={L.midY}>
		{@render props.buttonBuyBonus({ anchor: 0.5 })}
	</Container>

	{#if props.fsCounter && stateUi.freeSpinCounterShow}
		<Container x={L.W / 2} y={L.midY - T.hero / 2 - T.caps.h / 2 - 16}>
			<LabelFreeSpinCounter stacked />
		</Container>
	{/if}
</MainContainer>

<MenuPod
	buttonPayTable={props.buttonPayTable}
	buttonGameRules={props.buttonGameRules}
	buttonSettings={props.buttonSettings}
	buttonSoundSwitch={props.buttonSoundSwitch}
	buttonMenuClose={props.buttonMenuClose}
	x={L.barL + L.menuX}
	bottomY={L.midY - T.bar.h / 2 - 24}
/>
