<script lang="ts" module>
	export type EmitterEventFreeSpinCounter =
		| { type: 'freeSpinCounterShow' }
		| { type: 'freeSpinCounterHide' }
		| { type: 'freeSpinCounterUpdate'; current?: number; total?: number };
</script>

<script lang="ts">
	// Free-spin counter — a limestone plaque in the BOARD FRAME's outer material
	// (operator direction: align with the board's pale faceted stone, nothing ornate).
	// The count is the hero; each spent spin lands with a small impact pop and a brief
	// accent flare in the pool of light. SUPER identity lives in the accent color.
	import { onMount } from 'svelte';
	import { MainContainer } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { BitmapText, Container, Sprite } from 'pixi-svelte';
	import { stateBet, stateUi } from 'state-shared';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismNumStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor } from '../game/motion';

	const context = getContext();

	// counter art is 1180x683; the glass window is inset 0.154H on every side, so
	// the interior spans ±0.346H — text rows seat symmetrically about center
	const PANEL_W = SYMBOL_SIZE * 2.45;
	const PANEL_H = PANEL_W * (683 / 1180);
	const GOLD = 0xffd25e;
	const CYAN = 0x2bb8e8;
	const isSuper = $derived(stateBet.activeBetModeKey === 'SUPER');
	const accent = $derived(isSuper ? GOLD : CYAN);

	// centre of the plaque sits left of the board, aligned to the board's top edge.
	// The margin clears the FRAME ART, which extends well past boardLayout's width —
	// 0.75S read as almost touching on screen
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

	// HYDRATE FROM stateUi: this component unmounts on layout change (portrait hides it)
	// and its emitter subscription dies with it. The handlers mirror every value into
	// stateUi for exactly this moment — without hydration, a rotate-away-and-back
	// mid-feature remounted a blank hidden counter until the next updateFreeSpin (or
	// forever, on the feature's last spin).
	let show = $state(stateUi.freeSpinCounterShow);
	let current = $state(stateUi.freeSpinCounterCurrent);
	let total = $state(stateUi.freeSpinCounterTotal);
	let tickAtMs = $state(-1e9); // last time `current` advanced (drives the pop + glint)
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
				// a retrigger's award landing on the counter deserves the same beat as a
				// spent spin — the '+N' bump used to swap in with zero motion
				total = emitterEvent.total;
				tickAtMs = performance.now();
			}
		},
	});

	const secs = $derived(t / 1000);
	const tickAge = $derived((t - tickAtMs) / 1000);
	// each spent spin: the count lands with a small impact, never a screen-wide event
	const countScale = $derived.by(() => {
		const u = clamp01(tickAge / 0.34);
		return u < 1 ? 1.32 - 0.32 * EASE.impact(u) : 1;
	});
	// the pool of light flares briefly as the count ticks, then settles
	const tickFlare = $derived(tickAge < 0.5 ? 1 - tickAge / 0.5 : 0);
</script>

<MainContainer>
	<FadeContainer {show} {...position}>
		<!-- the limestone plaque (board-frame material, calm and architectural) -->
		<Sprite key="counterStone" anchor={0.5} width={PANEL_W} height={PANEL_H} />

		<!-- soft accent pool behind the count so the numerals sit in light, not on
		     glass; it flares briefly with each spent spin -->
		<Sprite
			key="mote"
			anchor={0.5}
			blendMode="add"
			tint={lerpColor(accent, 0xffffff, 0.35)}
			y={PANEL_H * 0.115}
			width={SYMBOL_SIZE * 1.5}
			height={SYMBOL_SIZE * 0.9}
			alpha={0.2 + 0.28 * tickFlare + 0.03 * Math.sin(secs * Math.PI * 0.7)}
		/>

		<!-- label voice + numeral font: the plaque reads as DATA (like the multiplier
		     chips), not as a shrunken celebration headline -->
		<BitmapText
			anchor={0.5}
			y={-PANEL_H * 0.115}
			text="FREE SPINS"
			style={superLabelStyle(SYMBOL_SIZE * 0.145, { align: 'center' })}
		/>
		<Container y={PANEL_H * 0.115} scale={countScale}>
			<BitmapText
				anchor={0.5}
				text={`${current} / ${total}`}
				style={prismNumStyle(SYMBOL_SIZE * 0.38, { align: 'center' })}
			/>
		</Container>
	</FadeContainer>
</MainContainer>
