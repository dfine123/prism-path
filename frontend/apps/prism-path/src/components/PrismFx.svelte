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
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';
	import { GlowFilter } from 'pixi-filters';
	import { Container, Sprite, BitmapText } from 'pixi-svelte';
	import { waitForTimeout } from 'utils-shared/wait';

	import { getContext } from '../game/context';
	import { getSymbolX, getSymbolY } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';

	const context = getContext();
	const glow = new GlowFilter({ color: 0x9a6bff, distance: 22, outerStrength: 4, innerStrength: 0 });

	// directional beast bust by facing direction
	const beastAsset = (d: Direction) =>
		({ up: 'beastUp', down: 'beastDown', left: 'beastLeft', right: 'beastRight' })[d];

	const key = (reel: number, row: number) => `${reel}-${row}`;
	const cellX = (reel: number) => getSymbolX(reel);
	// Math emits client (padded) rows where visible rows are 1..H; board renders 0..H-1 → -1.
	const cellY = (row: number) => getSymbolY(row - 1);

	// Persisted converted multiplier-wild cells (the beast's wake). Multiplier ACCUMULATES so an
	// overlap cell grows to the product as a second beast crosses it.
	let revealed = $state<Record<string, { reel: number; row: number; mult: number }>>({});
	// Beasts that have dropped and are waiting to fire (rendered facing their direction, NO mult).
	let dropped = $state<Record<string, { reel: number; row: number; direction: Direction }>>({});
	// The single beast currently travelling (only one fires at a time; events are sequential).
	let traveling = $state(false);
	let travelDir = $state<Direction>('down');

	const tx = new Tween(0, { duration: 165, easing: cubicOut });
	const ty = new Tween(0, { duration: 165, easing: cubicOut });

	const revealCell = (reel: number, row: number, mult: number) => {
		const k = key(reel, row);
		const prev = revealed[k];
		// accumulate: a second beast over the same cell multiplies (x2 -> x6)
		revealed[k] = { reel, row, mult: (prev?.mult ?? 1) * mult };
		revealed = { ...revealed };
	};

	context.eventEmitter.subscribeOnMount({
		// Beast drops onto its cell facing its direction — multiplier NOT shown yet.
		prismBeastShow: async (e) => {
			dropped[key(e.position.reel, e.position.row)] = {
				reel: e.position.reel,
				row: e.position.row,
				direction: e.direction,
			};
			dropped = { ...dropped };
			await waitForTimeout(360);
		},
		// Beast travels square-by-square in its facing direction, revealing each cell's multiplier as
		// it arrives, then transforms away at the edge (revealing the final square).
		prismPathShow: async (e) => {
			const k = key(e.source.reel, e.source.row);
			const beastMult = e.cells[0]?.multiplier ?? 1; // every cell carries this beast's own mult
			travelDir = dropped[k]?.direction ?? e.direction;
			delete dropped[k];
			dropped = { ...dropped };

			tx.set(cellX(e.source.reel), { duration: 0 });
			ty.set(cellY(e.source.row), { duration: 0 });
			traveling = true;
			await waitForTimeout(70);

			// own cell lights up as the beast departs
			revealCell(e.source.reel, e.source.row, beastMult);

			// travel the path, revealing each cell on arrival
			for (const c of e.cells) {
				await Promise.all([tx.set(cellX(c.position.reel)), ty.set(cellY(c.position.row))]);
				revealCell(c.position.reel, c.position.row, c.multiplier);
			}

			// reached the edge (or a whiff with no path): transform away
			await waitForTimeout(190);
			traveling = false;
		},
		prismClear: () => {
			revealed = {};
			dropped = {};
			traveling = false;
		},
	});
</script>

<Container
	x={context.stateGameDerived.boardLayout().x}
	y={context.stateGameDerived.boardLayout().y}
	pivot={context.stateGameDerived.boardLayout().pivot}
>
	<!-- converted multiplier wilds left in the beast's wake -->
	{#each Object.values(revealed) as cell (cell.reel + '-' + cell.row)}
		<Sprite
			key="WILD"
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
			style={{ fontFamily: 'gold', fontSize: 54 }}
		/>
	{/each}

	<!-- beasts that have dropped but not yet fired (facing their direction, no multiplier badge) -->
	{#each Object.values(dropped) as b (b.reel + '-' + b.row)}
		<Sprite
			key={beastAsset(b.direction)}
			x={cellX(b.reel)}
			y={cellY(b.row)}
			anchor={0.5}
			width={SYMBOL_SIZE}
			height={SYMBOL_SIZE}
			filters={[glow]}
		/>
	{/each}

	<!-- the travelling beast (directional bust; reveals the cells it passes) -->
	{#if traveling}
		<Sprite
			key={beastAsset(travelDir)}
			x={tx.current}
			y={ty.current}
			anchor={0.5}
			width={SYMBOL_SIZE}
			height={SYMBOL_SIZE}
			filters={[glow]}
		/>
	{/if}
</Container>
