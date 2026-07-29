<script lang="ts" module>
	export type EmitterEventFreeSpinCounter =
		| { type: 'freeSpinCounterShow' }
		| { type: 'freeSpinCounterHide' }
		| { type: 'freeSpinCounterUpdate'; current?: number; total?: number };
</script>

<script lang="ts">
	// Free-spin counter — code-drawn prism pill beside the board (no template atlas panel).
	import { MainContainer } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { BitmapText } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismNumStyle, superLabelStyle } from '../game/fonts';
	import PrismPanel from './PrismPanel.svelte';

	const context = getContext();

	const PANEL_W = SYMBOL_SIZE * 2.1;
	const PANEL_H = SYMBOL_SIZE * 1.15;
	// centre of the pill sits left of the board, aligned to the board's top edge
	const position = $derived({
		x:
			context.stateGameDerived.boardLayout().x -
			context.stateGameDerived.boardLayout().width * 0.5 -
			PANEL_W * 0.5 -
			SYMBOL_SIZE * 0.85,
		y:
			context.stateGameDerived.boardLayout().y -
			context.stateGameDerived.boardLayout().height * 0.5 +
			PANEL_H * 0.5,
	});

	let show = $state(false);
	let current = $state(0);
	let total = $state(0);

	context.eventEmitter.subscribeOnMount({
		freeSpinCounterShow: () => (show = true),
		freeSpinCounterHide: () => (show = false),
		freeSpinCounterUpdate: (emitterEvent) => {
			if (emitterEvent.current !== undefined) current = emitterEvent.current;
			if (emitterEvent.total !== undefined) total = emitterEvent.total;
		},
	});
</script>

<MainContainer>
	<FadeContainer {show} {...position}>
		<PrismPanel width={PANEL_W} height={PANEL_H} chamfer={14}>
			<!-- label voice + numeral font: the chip reads as DATA (like the multiplier
			     chips), not as a shrunken celebration headline -->
			<BitmapText
				anchor={0.5}
				y={-PANEL_H * 0.21}
				text="FREE SPIN"
				style={superLabelStyle(SYMBOL_SIZE * 0.19, { align: 'center' })}
			/>
			<BitmapText
				anchor={0.5}
				y={PANEL_H * 0.16}
				text={`${current} / ${total}`}
				style={prismNumStyle(SYMBOL_SIZE * 0.38, { align: 'center' })}
			/>
		</PrismPanel>
	</FadeContainer>
</MainContainer>
