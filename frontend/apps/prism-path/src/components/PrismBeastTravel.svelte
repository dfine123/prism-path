<script lang="ts" module>
	import type { Position } from '../game/types';

	// The Prism Beast travel overlay. Per dragon the math emits prismBeast (land/charge) then
	// prismPath (the fired path). The flight is ONE CONTINUOUS MOTION (single accelerating
	// curve seat -> cells -> off the board). The path light is drawn with the SAME shared
	// beam renderer as the persistent trail cells (game/trailBeam.ts), clipped by how far the
	// head has travelled — so when the cells take over at the flash, the pixels are identical
	// and the hand-off is invisible.
	export type BeastTravelDir = 'up' | 'down' | 'left' | 'right';
	export type BeastTravel = {
		direction: BeastTravelDir;
		sticky: boolean;
		multiplier: number;
		origin: Position;
		cells: { position: Position; multiplier: number }[];
	};
	export type EmitterEventPrismBeast =
		| { type: 'prismBeastCharge'; position: Position }
		| { type: 'prismBeastTravel'; beast: BeastTravel };
</script>

<script lang="ts">
	import { Sprite, Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { boardSlam, boardRubberBand } from '../game/stateFx.svelte';
	import { SYMBOL_SIZE, CELL_W, BOARD_DIMENSIONS } from '../game/constants';
	import { EASE, clamp01, lerp, paletteAt } from '../game/motion';
	import { drawTrailBeam, TRAIL_FLOW_HZ, TRAIL_HOT_FLIGHT } from '../game/trailBeam';

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

	// ---- feel tunables (dial these) ----
	const DRAGON_SCALE = 1.36; // projectile is bigger than the wilds it leaves
	const PER_CELL_MS = 88; // flow pace
	const TRAVEL_MIN_MS = 300;
	const EXIT_MS = 240; // off-board leg of the SAME motion
	const TAIL_MS = 200; // flash/glow settle after the wilds have landed
	const ACCEL = 1.35; // p = u^ACCEL — quiet start IS the charge; accelerates to exit
	const STRETCH = 0.6; // stretch along the motion axis while flowing (the "push")
	const EXIT_PUSH = 1.5; // off-board distance in cells along the travel axis

	let visible = $state(false);
	let asset = $state<string>('beastDown');
	let dragon = $state({ x: 0, y: 0, sx: 1, sy: 1, alpha: 0 });
	let glowAlpha = $state(0);
	let flash = $state({ x: 0, y: 0, r: 0, alpha: 0 });
	// the in-flight path light: per-cell beams clipped at headLen (same renderer as the cells)
	let ribbon = $state({ show: false, headLen: 0, headX: 0, headY: 0 });
	// geometry for the ribbon draw (plain ref — redraws are driven by ribbon state)
	let geomRef: {
		cells: { x: number; y: number }[];
		cellStart: number[];
		axisLen: number;
		horizontal: boolean;
		flowSign: number;
	} | null = null;

	const now = () => performance.now();

	const cellPos = (p: Position) => {
		const sym = board()[p.reel]?.reelState?.symbols?.[p.row];
		const y = sym && typeof sym.symbolY === 'function' ? sym.symbolY() : (p.row - 0.5) * SYMBOL_SIZE;
		return { x: getSymbolX(p.reel), y };
	};

	// Convert a covered cell to a trail wild (accumulating so an overlap grows to the product).
	// Cells land as ONE batch when the head completes the path — pixel-identical to the ribbon.
	// Seat rules (the math stamps every crossed cell with the per-beast-once PRODUCT, and the
	// on-board chip must agree):
	// - a beast's OWN sticky seat is exempt: the reveal seeded it (sticky + multiplier);
	//   accumulating would square it (seed x path-cell = 2x2).
	// - ANOTHER beast crossing a sticky seat DOES accumulate — the seat's lane pays the
	//   product, so a frozen chip would lie.
	// - an UNFIRED beast's seat crossed by an earlier flight accumulates the product but
	//   KEEPS its seated dragon (no trail flag) — converting it made the bust vanish before
	//   its own charge/flight choreography played. Its own flight later converts it.
	const revealCell = (
		reel: number,
		row: number,
		direction: string,
		mult: number,
		isOwnSeat: boolean,
	) => {
		const reelSymbol = board()[reel]?.reelState?.symbols?.[row];
		if (!reelSymbol) return;
		const raw = reelSymbol.rawSymbol;
		const prev = raw.multiplier ?? 1;
		if (raw.sticky) {
			if (!isOwnSeat) reelSymbol.rawSymbol = { ...raw, multiplier: prev * mult };
			reelSymbol.symbolState = 'land';
			return;
		}
		if (!isOwnSeat && raw.name === 'WILD' && !!raw.direction && !raw.trail) {
			reelSymbol.rawSymbol = { ...raw, multiplier: prev * mult };
			reelSymbol.symbolState = 'land';
			return;
		}
		reelSymbol.rawSymbol = {
			name: 'WILD',
			wild: true,
			direction,
			multiplier: prev * mult,
			trail: true,
		};
		reelSymbol.symbolState = 'land';
	};

	const runTravel = (beast: BeastTravel) =>
		new Promise<void>((resolve) => {
			const dir = beast.direction;
			asset = BEAST_ASSET[dir] ?? 'beastDown';
			const dv = DIRV[dir];
			const horizontal = dv.x !== 0;
			const axisLen = horizontal ? CELL_W : SYMBOL_SIZE;
			const flowSign = dir === 'left' || dir === 'up' ? -1 : 1;
			const origin = cellPos(beast.origin);
			const cellPts = beast.cells.length > 0 ? beast.cells.map((c) => cellPos(c.position)) : [origin];
			const last = cellPts[cellPts.length - 1];
			// ONE polyline: seat -> every covered cell -> off the board
			const exit = {
				x: last.x + dv.x * EXIT_PUSH * CELL_W,
				y: last.y + dv.y * EXIT_PUSH * SYMBOL_SIZE,
			};
			const pts = [...cellPts, exit];
			const cum = [0];
			for (let i = 1; i < pts.length; i++) {
				cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
			}
			const totalLen = Math.max(cum[cum.length - 1], 1);
			// the path light completes when the LAST cell is fully painted (its far edge)
			const revealAtLen = Math.min(cum[cellPts.length - 1] + axisLen / 2, totalLen);
			const DUR = Math.max(TRAVEL_MIN_MS, PER_CELL_MS * Math.max(1, cellPts.length - 1) + EXIT_MS);
			const total = DUR + TAIL_MS;
			const start = now();
			let revealedAll = false;
			let flashAt = -1;
			let exited = false;

			geomRef = {
				cells: cellPts,
				cellStart: cellPts.map((_, i) => Math.max(0, cum[i] - axisLen / 2)),
				axisLen,
				horizontal,
				flowSign,
			};

			// THE GLIDE — a LOOPING bed of moving air that runs for exactly as long as the
			// dragon is travelling. It starts here (push-off) and is stopped the moment the
			// flight ends, below. A one-shot could not cover flights whose length varies
			// with path length, and the once-player refuses to retrigger a cue that is
			// still sounding — which is why it sometimes never fired at all.
			context.eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_dragon_glide' });
			const stopGlide = () =>
				context.eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_dragon_glide' });

			visible = true;
			dragon = { x: origin.x, y: origin.y, sx: DRAGON_SCALE, sy: DRAGON_SCALE, alpha: 0 };
			glowAlpha = 0;
			flash = { x: last.x, y: last.y, r: 0, alpha: 0 };
			ribbon = { show: false, headLen: 0, headX: origin.x, headY: origin.y };

			const posAtLen = (L: number) => {
				for (let i = 1; i < pts.length; i++) {
					if (L <= cum[i] || i === pts.length - 1) {
						const t = clamp01((L - cum[i - 1]) / Math.max(cum[i] - cum[i - 1], 0.001));
						return { x: lerp(pts[i - 1].x, pts[i].x, t), y: lerp(pts[i - 1].y, pts[i].y, t) };
					}
				}
				return pts[pts.length - 1];
			};

			const applyStretch = (amt: number) => {
				const along = 1 + amt;
				const perp = 1 - 0.45 * amt;
				dragon.sx = DRAGON_SCALE * (horizontal ? along : perp);
				dragon.sy = DRAGON_SCALE * (horizontal ? perp : along);
			};

			const revealAll = () => {
				if (revealedAll) return;
				revealedAll = true;
				// the persistent cells take over the EXACT pixels the ribbon was drawing
				ribbon.show = false;
				// ONE cue for the ignition — the warm chord says it. (A second "explode"
				// layer under it just muddied the moment; two hits on one beat read as
				// clutter, not weight.)
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
				boardSlam(1); // full path ignites — the heaviest beat of the flight
				for (const c of beast.cells) {
					const isOwnSeat =
						c.position.reel === beast.origin.reel && c.position.row === beast.origin.row;
					revealCell(c.position.reel, c.position.row, dir, c.multiplier, isOwnSeat);
				}
				// a STICKY dragon that has flown does NOT re-hold its seat: the seat goes
				// dormant (renders as a trail cell inside the marker box) on the same beat
				// non-sticky seats convert, and the next reveal drops the dragon back in.
				// Done here (not per-cell) so a whiffed sticky — empty cells — vacates too.
				if (beast.sticky) {
					const seat = board()[beast.origin.reel]?.reelState?.symbols?.[beast.origin.row];
					if (seat?.rawSymbol.sticky) {
						seat.rawSymbol = { ...seat.rawSymbol, dormant: true };
					}
				}
			};

			const frame = () => {
				const el = now() - start;
				const u = clamp01(el / DUR);
				const p = Math.pow(u, ACCEL); // one curve: quiet charge -> accelerate -> gone
				const L = p * totalLen;
				const pos = posAtLen(L);

				// the dragon PUSHES PAST the edge: the board gives a few px in the exit
				// direction and rubber-bands back — momentum handed to the cabinet instead
				// of a hard clip at the mask
				if (
					!exited &&
					(pos.x < 0 ||
						pos.x > BOARD_DIMENSIONS.x * CELL_W ||
						pos.y < 0 ||
						pos.y > BOARD_DIMENSIONS.y * SYMBOL_SIZE)
				) {
					exited = true;
					stopGlide(); // it has cleared the edge — the motion is over
					boardRubberBand(dv.x, dv.y);
				}

				// materialize fast; stay OPAQUE while sliding under the border (the board-rect
				// mask does the exit) — only a late safety fade once it's already off-board
				const fadeIn = clamp01(el / 90);
				const fadeOut = 1 - EASE.collapse(clamp01((u - 0.92) / 0.08));
				dragon.x = pos.x;
				dragon.y = pos.y;
				dragon.alpha = fadeIn * fadeOut;
				glowAlpha = 0.85 * fadeIn * fadeOut;

				// body: brief coil at the very start, then stretch ramps up and HOLDS to the exit
				const squash = u < 0.12 ? -0.16 * (1 - u / 0.12) : 0;
				const str = STRETCH * clamp01((u - 0.08) / 0.3);
				applyStretch(squash + str);

				// path light: grows with the head, capped at the wilds' span
				if (el > 30 && !revealedAll) {
					ribbon.show = true;
					ribbon.headLen = Math.min(L, revealAtLen);
					const hp = posAtLen(Math.min(L, revealAtLen));
					ribbon.headX = hp.x;
					ribbon.headY = hp.y;
				}

				// the head completes the path: flash + the wilds take over seamlessly
				if (L >= revealAtLen && flashAt < 0) {
					flashAt = el;
					revealAll();
				}
				if (flashAt >= 0) {
					const ft = clamp01((el - flashAt) / 300);
					flash = {
						x: last.x,
						y: last.y,
						r: EASE.impact(ft) * SYMBOL_SIZE * 1.15,
						alpha: (1 - ft) * 0.85,
					};
				}

				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					// safety: every cell resolved before handing back control
					revealAll();
					stopGlide(); // safety: a whiffed flight never crosses an edge
					dragon.alpha = 0;
					glowAlpha = 0;
					flash = { ...flash, alpha: 0 };
					ribbon.show = false;
					visible = false;
					geomRef = null;
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
	<!-- in-flight path light: the SAME beam renderer as the persistent cells, clipped by
	     head coverage — plus a bright comet cap at the head -->
	<Graphics
		blendMode="add"
		draw={(g) => {
			if (!ribbon.show || !geomRef) return;
			const G = geomRef;
			const phase = (performance.now() / 1000) * TRAIL_FLOW_HZ;
			for (let i = 0; i < G.cells.length; i++) {
				const cov = ribbon.headLen - G.cellStart[i];
				if (cov <= 1) continue;
				const a = G.axisLen;
				const c = Math.min(cov, a);
				const clipFrom = G.flowSign > 0 ? -a / 2 : a / 2 - c;
				const clipTo = G.flowSign > 0 ? -a / 2 + c : a / 2;
				drawTrailBeam(g, {
					cx: G.cells[i].x,
					cy: G.cells[i].y,
					horizontal: G.horizontal,
					flowSign: G.flowSign,
					phase,
					hot: TRAIL_HOT_FLIGHT,
					clipFrom,
					clipTo,
				});
			}
			// comet cap where the light is being written
			g.circle(ribbon.headX, ribbon.headY, SYMBOL_SIZE * 0.28).fill({ color: 0xffffff, alpha: 0.4 });
			g.circle(ribbon.headX, ribbon.headY, SYMBOL_SIZE * 0.5).fill({ color: paletteAt(-phase), alpha: 0.2 });
		}}
	/>

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

	<!-- path-complete burst ring -->
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
