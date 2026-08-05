<script lang="ts" module>
	export type EmitterEventFreeSpinCounter =
		| { type: 'freeSpinCounterShow' }
		| { type: 'freeSpinCounterHide' }
		| { type: 'freeSpinCounterUpdate'; current?: number; total?: number };
</script>

<script lang="ts">
	// Free-spin counter — a MINIATURE of the win-box family (the game's approved
	// dialog design): small opaque violet plaque with the accent light pool, no
	// jewellery (operator: gems dropped). The count is the hero; each spent spin
	// (and a retrigger's total bump) lands with a small impact pop and an accent
	// flare. SUPER rides gold.
	import { onMount } from 'svelte';
	import { MainContainer } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { BitmapText, Container, Sprite } from 'pixi-svelte';
	import { stateBet, stateUi } from 'state-shared';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismNumStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';

	const context = getContext();

	const PANEL_W = SYMBOL_SIZE * 2.2;
	const PANEL_H = SYMBOL_SIZE * 1.25;
	const GOLD = 0xffd25e;
	const CYAN = 0x2bb8e8;
	const isSuper = $derived(stateBet.activeBetModeKey === 'SUPER');
	const accent = $derived(isSuper ? GOLD : CYAN);

	// centre of the plaque sits left of the board, aligned to the board's top edge
	const position = $derived({
		x:
			context.stateGameDerived.boardLayout().x -
			context.stateGameDerived.boardLayout().width * 0.5 -
			PANEL_W * 0.5 -
			SYMBOL_SIZE * 1.2,
		y:
			context.stateGameDerived.boardLayout().y -
			context.stateGameDerived.boardLayout().height * 0.5 +
			PANEL_H * 0.5,
	});

	// HYDRATE FROM stateUi: this component unmounts on layout change (portrait hides
	// it) and its emitter subscription dies with it — hydration survives the remount.
	let show = $state(stateUi.freeSpinCounterShow);
	let current = $state(stateUi.freeSpinCounterCurrent);
	let total = $state(stateUi.freeSpinCounterTotal);
	let tickAtMs = $state(-1e9);
	let t = $state(0);

	onMount(() => {
		let raf = 0;
		const frame = () => {
			t = performance.now();
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	context.eventEmitter.subscribeOnMount({
		freeSpinCounterShow: () => (show = true),
		freeSpinCounterHide: () => (show = false),
		freeSpinCounterUpdate: (emitterEvent) => {
			if (emitterEvent.current !== undefined && emitterEvent.current !== current) {
				current = emitterEvent.current;
				tickAtMs = performance.now();
			}
			if (emitterEvent.total !== undefined && emitterEvent.total !== total) {
				// a retrigger's award landing on the counter deserves the same beat
				total = emitterEvent.total;
				tickAtMs = performance.now();
			}
		},
	});

	const secs = $derived(t / 1000);
	const tickAge = $derived((t - tickAtMs) / 1000);
	const countScale = $derived.by(() => {
		const u = clamp01(tickAge / 0.34);
		return u < 1 ? 1.32 - 0.32 * EASE.impact(u) : 1;
	});
	const tickFlare = $derived(tickAge < 0.5 ? 1 - tickAge / 0.5 : 0);
</script>

<MainContainer>
	<FadeContainer {show} {...position}>
		<PrismPanel width={PANEL_W} height={PANEL_H} {accent} opaque chamfer={14}>
			<!-- accent pool behind the count; flares briefly with each spent spin -->
			<Sprite
				key="mote"
				anchor={0.5}
				blendMode="add"
				tint={lerpColor(accent, 0xffffff, 0.35)}
				y={PANEL_H * 0.12}
				width={SYMBOL_SIZE * 1.5}
				height={SYMBOL_SIZE * 0.9}
				alpha={0.22 + 0.26 * tickFlare + 0.03 * Math.sin(secs * Math.PI * 0.7)}
			/>
			<BitmapText
				anchor={0.5}
				y={-PANEL_H * 0.22}
				text="FREE SPINS"
				style={superLabelStyle(SYMBOL_SIZE * 0.16, { align: 'center' })}
			/>
			<Container y={PANEL_H * 0.16} scale={countScale}>
				<BitmapText
					anchor={0.5}
					text={`${current} / ${total}`}
					style={prismNumStyle(SYMBOL_SIZE * 0.4, { align: 'center' })}
				/>
			</Container>
		</PrismPanel>
	</FadeContainer>
</MainContainer>
