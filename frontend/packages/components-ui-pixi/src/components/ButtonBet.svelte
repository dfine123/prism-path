<script lang="ts">
	import { Container, Graphics, Text } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';
	import { OnHotkey } from 'components-shared';
	import { stateBetDerived, stateModal, stateUi } from 'state-shared';

	import UiGlass from './UiGlass.svelte';
	import UiGlyph from './UiGlyph.svelte';
	import ButtonBetProvider from './ButtonBetProvider.svelte';
	import { getContext } from '../context';
	import { i18nDerived } from '../i18n/i18nDerived';
	import { SUPER_UI, prismAt, lerpColor } from '../theme';

	// THE HERO. The one control the player touches a thousand times: biggest silhouette,
	// the only prism-gradient ring in the console, docked at the action end of the rail.
	// SPIN glyph + label while idle, STOP square while the reels run.
	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const T = SUPER_UI;
	// bet-cost gates only the SPIN meaning — mid-round the button means STOP and must stay
	// live even when the post-wager balance dips below the bet cost. Any open overlay
	// (DOM modal / menu pod / press-anywhere catcher) kills both press and Space — no
	// bets behind a modal, and no double meaning while a PRESS TO CONTINUE owns the press.
	const overlayOpen = $derived(
		stateModal.modal !== null || stateUi.menuOpen || stateUi.pressCatcherActive,
	);
	const disabled = $derived(
		overlayOpen || (context.stateXstateDerived.isIdle() && !stateBetDerived.isBetCostAvailable()),
	);
	const D = T.hero;
	const sizes = { width: D, height: D };
	const RING_SEGS = 48;
	const ringR = D / 2 - 4;
	const ringW = D * 0.055;
</script>

<ButtonBetProvider>
	{#snippet children({ key, onpress })}
		{@const isSpin = ['spin_default', 'spin_disabled'].includes(key)}
		{@const keyDisabled = disabled || ['spin_disabled', 'stop_disabled'].includes(key)}
		<OnHotkey hotkey="Space" {disabled} {onpress} />
		<Button {...props} {sizes} {onpress} {disabled}>
			{#snippet children({ center, hovered, pressed })}
				<Container {...center} scale={pressed ? T.press : 1} alpha={keyDisabled ? T.dim : 1}>
					<!-- OPAQUE BASE: a solid disc under the whole hero — the deck's end cap,
					     seam and scene can never show through the button (no see-through gaps) -->
					<Graphics
						draw={(g) => {
							g.circle(0, 0, ringR + ringW * 0.95).fill({ color: 0x0d0817, alpha: 1 });
							g.circle(0, 0, ringR + ringW * 0.95).stroke({ width: 3.5, color: 0x080510, alpha: 0.92 });
						}}
					/>
					<UiGlass width={D - ringW * 3} height={D - ringW * 3} radius={D / 2} tone="hero" lit={!keyDisabled && hovered} />
					<!-- JEWEL BEZEL: the prism ring sits between two dark bezel rings, with a
					     gloss crescent on the core — a set stone, not a painted stripe.
					     Every arc gets an explicit moveTo (no stray path-connector lines). -->
					<Graphics
						draw={(g) => {
							g.circle(0, 0, ringR + ringW * 0.78).stroke({ width: 3, color: 0x080510, alpha: 0.9 });
							g.circle(0, 0, ringR - ringW * 0.78).stroke({ width: 3, color: 0x080510, alpha: 0.9 });
							for (let i = 0; i < RING_SEGS; i++) {
								const a0 = (i / RING_SEGS) * Math.PI * 2 - Math.PI / 2;
								const a1 = ((i + 1.15) / RING_SEGS) * Math.PI * 2 - Math.PI / 2;
								const col = prismAt(i / RING_SEGS);
								g.moveTo(Math.cos(a0) * ringR, Math.sin(a0) * ringR);
								g.arc(0, 0, ringR, a0, a1).stroke({
									width: ringW,
									color: hovered && !keyDisabled ? lerpColor(col, 0xffffff, 0.25) : col,
									cap: 'butt',
								});
							}
							// core gloss crescent
							const gr = D / 2 - ringW * 2.4;
							const ga = -Math.PI * 0.88;
							g.moveTo(Math.cos(ga) * gr, Math.sin(ga) * gr);
							g.arc(0, 0, gr, ga, -Math.PI * 0.14).stroke({
								width: 5,
								color: 0xffffff,
								alpha: 0.11,
								cap: 'round',
							});
						}}
					/>
					<UiGlyph icon={isSpin ? 'spin' : 'stop'} shadow y={-D * 0.075} size={D * 0.4} />
					<Text
						anchor={0.5}
						y={D * 0.21}
						text={isSpin ? i18nDerived.bet() : i18nDerived.stop()}
						style={{
							align: 'center',
							fontFamily: T.font,
							fontWeight: '700',
							fontSize: T.fs.heroLabel,
							fill: T.color.text,
						}}
					/>
				</Container>
			{/snippet}
		</Button>
	{/snippet}
</ButtonBetProvider>
