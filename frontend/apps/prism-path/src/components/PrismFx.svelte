<script lang="ts" module>
	import type { Position } from '../game/types';

	type Direction = 'up' | 'down' | 'left' | 'right';

	export type EmitterEventPrismFx =
		| {
				type: 'prismBeastShow';
				position: Position;
				direction: Direction;
				multiplier: number;
				whiff: boolean;
		  }
		| {
				type: 'prismPathShow';
				source: Position;
				direction: Direction;
				cells: { position: Position; multiplier: number }[];
		  }
		| { type: 'prismClear' };
</script>

<script lang="ts">
	import { GlowFilter } from 'pixi-filters';
	import { Container, Sprite, BitmapText } from 'pixi-svelte';
	import { waitForTimeout } from 'utils-shared/wait';

	import { getContext } from '../game/context';
	import { getSymbolX, getSymbolY } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';

	const context = getContext();
	// pixi-filters glow for the multiplier-wild conversion (Phase-1 stub; Spine rig replaces later).
	const glow = new GlowFilter({ color: 0x9a6bff, distance: 22, outerStrength: 4, innerStrength: 0 });

	type Cell = { reel: number; row: number; mult: number; isBeast: boolean };
	// One overlay per cell (keyed reel-row) so an overlap cell shows a single BEAST/WILD tile and a
	// single product badge instead of stacked beast+path overlays.
	let cells = $state<Record<string, Cell>>({});

	const put = (reel: number, row: number, mult: number, isBeast: boolean) => {
		const key = `${reel}-${row}`;
		const prev = cells[key];
		cells[key] = {
			reel,
			row,
			mult: Math.max(mult, prev?.mult ?? 0), // overlap product wins over a single beast's value
			isBeast: isBeast || (prev?.isBeast ?? false),
		};
		cells = { ...cells };
	};

	// Math emits client (padded) rows where visible rows are 1..H; the board renders visible
	// rows via getSymbolY(0..H-1). Convert: visibleRow = clientRow - 1.
	const cellX = (reel: number) => getSymbolX(reel);
	const cellY = (row: number) => getSymbolY(row - 1);

	context.eventEmitter.subscribeOnMount({
		// Resolve after the stub timing so the book sequencer advances to winInfo, but KEEP the
		// overlay visible through the win. prismClear (fired on the next reveal) resets it.
		prismBeastShow: async (emitterEvent) => {
			put(emitterEvent.position.reel, emitterEvent.position.row, emitterEvent.multiplier, true);
			await waitForTimeout(emitterEvent.whiff ? 450 : 650);
		},
		prismPathShow: async (emitterEvent) => {
			for (const c of emitterEvent.cells) put(c.position.reel, c.position.row, c.multiplier, false);
			await waitForTimeout(850);
		},
		prismClear: () => {
			cells = {};
		},
	});
</script>

<Container
	x={context.stateGameDerived.boardLayout().x}
	y={context.stateGameDerived.boardLayout().y}
	pivot={context.stateGameDerived.boardLayout().pivot}
>
	{#each Object.values(cells) as cell (cell.reel + '-' + cell.row)}
		<Sprite
			key={cell.isBeast ? 'prismBeast' : 'WILD'}
			x={cellX(cell.reel)}
			y={cellY(cell.row)}
			anchor={0.5}
			width={SYMBOL_SIZE}
			height={SYMBOL_SIZE}
			filters={[glow]}
		/>
		<BitmapText
			anchor={0.5}
			x={cellX(cell.reel)}
			y={cellY(cell.row)}
			text={`${cell.mult}X`}
			style={{ fontFamily: 'gold', fontSize: cell.isBeast ? 60 : 52 }}
		/>
	{/each}
</Container>
