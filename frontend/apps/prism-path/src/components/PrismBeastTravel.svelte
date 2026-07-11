<script lang="ts" module>
	// The Prism Beast travel overlay. The math emits, per new beast, a prismBeast (land/charge)
	// then a prismPath (own cell -> path to the edge). This overlay owns the *feel*: the dragon
	// winds up, PUSHES off with a squash-stretch, FLOWS along the path trailing prismatic
	// afterimages, drops a multiplier wild into each cell as it passes, and bursts off the edge.
	export type BeastTravelDir = 'up' | 'down' | 'left' | 'right';
	export type BeastTravel = {
		direction: BeastTravelDir;
		whiff: boolean;
		cells: { position: { reel: number; row: number }; multiplier: number }[];
	};
	export type EmitterEventPrismBeast =
		| { type: 'prismBeastCharge'; position: { reel: number; row: number } }
		| { type: 'prismBeastTravel'; beast: BeastTravel };
</script>

<script lang="ts">
	import { Sprite, Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import { EASE, clamp01, lerp } from '../game/motion';

	const context = getContext();
	const board = () => context.stateGame.board;

	const BEAST_ASSET: Record<BeastTravelDir, string> = {
		up: 'beastUp',
		down: 'beastDown',
		left: 'beastLeft',
		right: 'beastRight',
	};
	const DIRV: Record<BeastTravelDir, { x: number; y: number }> = {
		up: { x: 0, y: -1 },
		down: { x: 0, y: 1 },
		left: { x: -1, y: 0 },
		right: { x: 1, y: 0 },
	};
	// prism-hued trail so the streak reads as refracted light, not a grey blur.
	const PRISM_TINTS = [0xff5db1, 0x2bb8e8, 0x3cc85a, 0x9b3ce8, 0xffd25e];

	// ---- feel tunables (dial these) ----
	const DRAGON_SCALE = 1.36; // projectile is bigger than the wilds it leaves
	const WINDUP_MS = 155; // anticipation: rear back before the push
	const PER_CELL_MS = 78; // flow speed
	const TRAVEL_MIN_MS = 175;
	const BURST_MS = 235; // push off the edge + dissipate
	const STRETCH = 0.6; // squash-stretch amount at peak flow (the "push")
	const REAR_BACK = 0.2; // how far it pulls back during wind-up (x symbol)
	const EXIT_PUSH = 1.05; // how far past the edge it flies on the burst (x symbol)
	const TRAIL_SPAWN_MS = 22;
	const TRAIL_LIFE_MS = 260;

	type After = {
		id: number;
		x: number;
		y: number;
		sx: number;
		sy: number;
		tint: number;
		asset: string;
		born: number;
		alpha: number;
	};

	let visible = $state(false);
	let asset = $state<string>('beastDown');
	let dragon = $state({ x: 0, y: 0, sx: 1, sy: 1, alpha: 0 });
	let glowAlpha = $state(0);
	let afters = $state<After[]>([]);
	let flash = $state({ x: 0, y: 0, r: 0, alpha: 0 });
	let afterSeq = 0;

	const now = () => performance.now();

	const cellPos = (reel: number, row: number) => {
		const sym = board()[reel]?.reelState?.symbols?.[row];
		const y = sym && typeof sym.symbolY === 'function' ? sym.symbolY() : (row - 0.5) * SYMBOL_SIZE;
		return { x: getSymbolX(reel), y };
	};

	// Drop a multiplier wild into a cell (accumulating so an overlap grows to the product), pop it.
	const revealCell = (reel: number, row: number, direction: string, mult: number) => {
		const reelSymbol = board()[reel]?.reelState?.symbols?.[row];
		if (!reelSymbol) return;
		const prev = reelSymbol.rawSymbol.multiplier ?? 1;
		reelSymbol.rawSymbol = {
			name: 'WILD',
			wild: true,
			direction,
			// accumulate: an overlap cell grows to the PRODUCT (x2 crossed by x3 -> x6)
			multiplier: prev * mult,
		};
		reelSymbol.symbolState = 'land';
		context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
	};

	const runTravel = (beast: BeastTravel) =>
		new Promise<void>((resolve) => {
			const dir = beast.direction;
			asset = BEAST_ASSET[dir] ?? 'beastDown';
			const dv = DIRV[dir];
			const horizontal = dv.x !== 0;
			const pts = beast.cells.map((c) => cellPos(c.position.reel, c.position.row));
			const mults = beast.cells.map((c) => c.multiplier);
			const N = pts.length;
			const origin = pts[0];
			const travelMs = Math.max(TRAVEL_MIN_MS, PER_CELL_MS * Math.max(1, N - 1));
			const total = WINDUP_MS + travelMs + BURST_MS;
			const start = now();
			let lastTrail = start;
			let revealed = new Set<number>();

			visible = true;
			afters = [];
			dragon = { x: origin.x, y: origin.y, sx: DRAGON_SCALE, sy: DRAGON_SCALE, alpha: 0 };
			glowAlpha = 0;
			flash = { x: origin.x, y: origin.y, r: 0, alpha: 0 };

			// point at eased progress p in [0,1] along the polyline (origin -> ... -> edge cell)
			const posAt = (p: number) => {
				if (N === 1) return { x: origin.x + dv.x * p * SYMBOL_SIZE * 0.6, y: origin.y + dv.y * p * SYMBOL_SIZE * 0.6 };
				const f = clamp01(p) * (N - 1);
				const i = Math.min(N - 2, Math.floor(f));
				const t = f - i;
				return { x: lerp(pts[i].x, pts[i + 1].x, t), y: lerp(pts[i].y, pts[i + 1].y, t) };
			};

			const ageTrail = (t: number) => {
				for (const a of afters) a.alpha = Math.max(0, 1 - (t - a.born) / TRAIL_LIFE_MS);
				afters = afters.filter((a) => a.alpha > 0.02);
			};

			const spawnTrail = (t: number, stretch: number) => {
				if (t - lastTrail < TRAIL_SPAWN_MS) return;
				lastTrail = t;
				afters.push({
					id: afterSeq++,
					x: dragon.x,
					y: dragon.y,
					sx: dragon.sx * 0.94,
					sy: dragon.sy * 0.94,
					tint: PRISM_TINTS[afterSeq % PRISM_TINTS.length],
					asset,
					born: t,
					alpha: 0.55,
				});
				afters = afters;
			};

			const applyStretch = (amt: number) => {
				const along = 1 + amt;
				const perp = 1 - 0.45 * amt;
				dragon.sx = DRAGON_SCALE * (horizontal ? along : perp);
				dragon.sy = DRAGON_SCALE * (horizontal ? perp : along);
			};

			const frame = () => {
				const el = now() - start;
				const t = now();

				if (el < WINDUP_MS) {
					// ANTICIPATION — fade in, pull back opposite the fire direction, coil up.
					const wp = EASE.load(clamp01(el / WINDUP_MS));
					dragon.alpha = wp;
					dragon.x = origin.x - dv.x * REAR_BACK * SYMBOL_SIZE * wp;
					dragon.y = origin.y - dv.y * REAR_BACK * SYMBOL_SIZE * wp;
					applyStretch(-0.12 * wp); // coil = slight squash
					glowAlpha = 0.5 * wp;
				} else if (el < WINDUP_MS + travelMs) {
					// PUSH + FLOW — launch along the path, body stretched by flow speed.
					if (!revealed.has(0)) {
						revealCell(beast.cells[0].position.reel, beast.cells[0].position.row, dir, mults[0]);
						revealed.add(0);
					}
					const tp = clamp01((el - WINDUP_MS) / travelMs);
					const p = EASE.glide(tp);
					const pos = posAt(p);
					dragon.x = pos.x;
					dragon.y = pos.y;
					dragon.alpha = 1;
					glowAlpha = 0.85;
					// stretch envelope peaks mid-flow -> reads as a push that eases out
					applyStretch(STRETCH * Math.sin(Math.PI * tp));
					spawnTrail(t, STRETCH);
					// drop a wild into each cell the head has reached
					if (N > 1) {
						const reachedUpto = Math.floor(p * (N - 1) + 0.001);
						for (let i = 1; i <= Math.min(reachedUpto, N - 1); i++) {
							if (!revealed.has(i)) {
								revealCell(beast.cells[i].position.reel, beast.cells[i].position.row, dir, mults[i]);
								revealed.add(i);
							}
						}
					}
				} else {
					// BURST — push off the board edge and dissipate; ring flash at the last cell.
					const bp = clamp01((el - WINDUP_MS - travelMs) / BURST_MS);
					const edge = posAt(1);
					const ee = EASE.settle(bp);
					dragon.x = edge.x + dv.x * EXIT_PUSH * SYMBOL_SIZE * ee;
					dragon.y = edge.y + dv.y * EXIT_PUSH * SYMBOL_SIZE * ee;
					dragon.alpha = 1 - EASE.collapse(bp);
					applyStretch(STRETCH * (1 - bp)); // stay stretched as it exits, relax as it fades
					glowAlpha = 0.85 * (1 - bp);
					flash = {
						x: edge.x,
						y: edge.y,
						r: EASE.impact(bp) * SYMBOL_SIZE * 1.15,
						alpha: (1 - bp) * 0.85,
					};
					// make sure the final cell is dropped
					for (let i = 0; i < N; i++) {
						if (!revealed.has(i)) {
							revealCell(beast.cells[i].position.reel, beast.cells[i].position.row, dir, mults[i]);
							revealed.add(i);
						}
					}
				}

				ageTrail(t);

				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					// safety: guarantee every cell is a resolved wild before we hand back control
					for (let i = 0; i < N; i++) {
						if (!revealed.has(i)) revealCell(beast.cells[i].position.reel, beast.cells[i].position.row, dir, mults[i]);
					}
					dragon.alpha = 0;
					glowAlpha = 0;
					flash = { ...flash, alpha: 0 };
					afters = [];
					visible = false;
					resolve();
				}
			};

			requestAnimationFrame(frame);
		});

	context.eventEmitter.subscribeOnMount({
		prismBeastTravel: async ({ beast }) => {
			await runTravel(beast);
		},
	});
</script>

{#if visible}
	<!-- prismatic afterimage trail (additive glow) -->
	{#each afters as a (a.id)}
		<Sprite
			key={a.asset}
			anchor={0.5}
			x={a.x}
			y={a.y}
			width={SYMBOL_SIZE * a.sx}
			height={SYMBOL_SIZE * a.sy}
			alpha={a.alpha}
			tint={a.tint}
			blendMode="add"
		/>
	{/each}

	<!-- soft glow under the head -->
	{#if glowAlpha > 0}
		<Sprite
			key={asset}
			anchor={0.5}
			x={dragon.x}
			y={dragon.y}
			width={SYMBOL_SIZE * dragon.sx * 1.35}
			height={SYMBOL_SIZE * dragon.sy * 1.35}
			alpha={glowAlpha * 0.4}
			tint={0xbfe9ff}
			blendMode="add"
		/>
	{/if}

	<!-- edge burst ring -->
	{#if flash.alpha > 0}
		<Graphics
			x={flash.x}
			y={flash.y}
			draw={(g) => {
				g.circle(0, 0, flash.r).stroke({ width: 5, color: 0xffffff, alpha: flash.alpha });
				g.circle(0, 0, flash.r * 0.55).fill({ color: 0xbfe9ff, alpha: flash.alpha * 0.3 });
			}}
		/>
	{/if}

	<!-- the dragon head -->
	<Sprite
		key={asset}
		anchor={0.5}
		x={dragon.x}
		y={dragon.y}
		width={SYMBOL_SIZE * dragon.sx}
		height={SYMBOL_SIZE * dragon.sy}
		alpha={dragon.alpha}
	/>
{/if}
