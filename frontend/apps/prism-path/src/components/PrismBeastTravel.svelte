<script lang="ts" module>
	import type { Position } from '../game/types';

	// The Prism Beast travel overlay. Per dragon the math emits prismBeast (land/charge) then
	// prismPath (the fired path). The flight is ONE CONTINUOUS MOTION: a single accelerating
	// curve (p = u^ACCEL) from the seat, through every covered cell, and straight off the
	// board — the quiet first frames ARE the charge, and it never brakes. The prism ribbon
	// streams behind the head (capped at the wilds' span); when the head crosses the last
	// cell the wilds land as ONE batch under the flash, and the ribbon drains after the
	// dragon has left.
	export type BeastTravelDir = 'up' | 'down' | 'left' | 'right';
	export type BeastTravel = {
		direction: BeastTravelDir;
		whiff: boolean;
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
	import { SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { EASE, clamp01, lerp, paletteAt } from '../game/motion';

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
	const PER_CELL_MS = 88; // flow pace (single continuous motion, so slightly richer per cell)
	const TRAVEL_MIN_MS = 300;
	const EXIT_MS = 240; // extra time budget for the off-board leg of the SAME motion
	const TAIL_MS = 330; // ribbon drain after the dragon has left
	const ACCEL = 1.35; // p = u^ACCEL — slow first frames ARE the charge; accelerates to exit
	const STRETCH = 0.6; // stretch along the motion axis while flowing (the "push")
	const EXIT_PUSH = 1.5; // how far past the last cell it flies off the board (x symbol)
	// ribbon
	const TRAIL_W_HEAD = 0.56;
	const TRAIL_W_TAIL = 0.16;
	const TRAIL_FLOW_HZ = 0.9;
	const TRAIL_TUCK = 0.2;

	let visible = $state(false);
	let asset = $state<string>('beastDown');
	let dragon = $state({ x: 0, y: 0, sx: 1, sy: 1, alpha: 0 });
	let glowAlpha = $state(0);
	let flash = $state({ x: 0, y: 0, r: 0, alpha: 0 });
	let trail = $state({ show: false, tailX: 0, tailY: 0, headX: 0, headY: 0, phase: 0, alpha: 0, drain: 0 });

	const now = () => performance.now();

	const cellPos = (p: Position) => {
		const sym = board()[p.reel]?.reelState?.symbols?.[p.row];
		const y = sym && typeof sym.symbolY === 'function' ? sym.symbolY() : (p.row - 0.5) * SYMBOL_SIZE;
		return { x: getSymbolX(p.reel), y };
	};

	// Convert a covered cell to a trail wild (accumulating so an overlap grows to the product).
	// Cells land as ONE batch under the flash — the flight itself never mutates the board.
	const revealCell = (reel: number, row: number, direction: string, mult: number) => {
		const reelSymbol = board()[reel]?.reelState?.symbols?.[row];
		if (!reelSymbol) return;
		const prev = reelSymbol.rawSymbol.multiplier ?? 1;
		reelSymbol.rawSymbol = {
			name: 'WILD',
			wild: true,
			direction,
			multiplier: prev * mult,
		};
		reelSymbol.symbolState = 'land';
	};

	const runTravel = (beast: BeastTravel) =>
		new Promise<void>((resolve) => {
			const dir = beast.direction;
			asset = BEAST_ASSET[dir] ?? 'beastDown';
			const dv = DIRV[dir];
			const horizontal = dv.x !== 0;
			const origin = cellPos(beast.origin);
			const cellPts = beast.cells.length > 0 ? beast.cells.map((c) => cellPos(c.position)) : [origin];
			const last = cellPts[cellPts.length - 1];
			// ONE polyline: seat -> every covered cell -> off the board (the exit is part of
			// the same motion, not a second push)
			// off-board distance in CELL units along the travel axis (cells are rectangular)
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
			const cellsEndLen = cum[pts.length - 2]; // arc length at the LAST covered cell
			// whiff (single cell): the wild lands as the dragon clears its own square
			const revealAtLen = Math.max(cellsEndLen, SYMBOL_SIZE * 0.45);
			const ribbonMaxLen = Math.min(cellsEndLen + 0.18 * SYMBOL_SIZE, totalLen);
			const DUR = Math.max(TRAVEL_MIN_MS, PER_CELL_MS * Math.max(1, cellPts.length - 1) + EXIT_MS);
			const total = DUR + TAIL_MS;
			const start = now();
			let revealedAll = false;
			let flashAt = -1;

			visible = true;
			dragon = { x: origin.x, y: origin.y, sx: DRAGON_SCALE, sy: DRAGON_SCALE, alpha: 0 };
			glowAlpha = 0;
			flash = { x: last.x, y: last.y, r: 0, alpha: 0 };
			trail = { show: false, tailX: origin.x, tailY: origin.y, headX: origin.x, headY: origin.y, phase: 0, alpha: 0, drain: 0 };

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
				context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
				for (const c of beast.cells) {
					revealCell(c.position.reel, c.position.row, dir, c.multiplier);
				}
			};

			const frame = () => {
				const el = now() - start;
				trail.phase = (el / 1000) * TRAIL_FLOW_HZ;
				const u = clamp01(el / DUR);
				const p = Math.pow(u, ACCEL); // one curve: quiet charge -> accelerate -> gone
				const L = p * totalLen;
				const pos = posAtLen(L);

				// materialize fast; dissolve over the exit leg WHILE STILL MOVING (never brakes)
				const fadeIn = clamp01(el / 90);
				const fadeOut = 1 - EASE.collapse(clamp01((u - 0.84) / 0.16));
				dragon.x = pos.x;
				dragon.y = pos.y;
				dragon.alpha = fadeIn * fadeOut;
				glowAlpha = 0.85 * fadeIn * fadeOut;

				// body: brief coil at the very start, then stretch ramps up and HOLDS to the exit
				const squash = u < 0.12 ? -0.16 * (1 - u / 0.12) : 0;
				const str = STRETCH * clamp01((u - 0.08) / 0.3);
				applyStretch(squash + str);

				// ribbon: streams behind the head, capped at the wilds' span
				if (el > 30 && el <= DUR) {
					trail.show = true;
					trail.alpha = clamp01((el - 30) / 90);
					const hl = Math.min(L - TRAIL_TUCK * SYMBOL_SIZE, ribbonMaxLen);
					if (hl > 2) {
						const hp = posAtLen(hl);
						trail.headX = hp.x;
						trail.headY = hp.y;
					}
				}

				// the head crosses the last cell: flash + the wilds land as one batch
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

				// after the dragon has left: the ribbon drains after it
				if (el > DUR) {
					const tt = clamp01((el - DUR) / TAIL_MS);
					trail.headX = posAtLen(ribbonMaxLen).x;
					trail.headY = posAtLen(ribbonMaxLen).y;
					trail.drain = EASE.collapse(clamp01((tt - 0.08) / 0.92));
					trail.alpha = 1 - EASE.collapse(clamp01((tt - 0.3) / 0.7));
				}

				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					// safety: every cell resolved before handing back control
					revealAll();
					dragon.alpha = 0;
					glowAlpha = 0;
					flash = { ...flash, alpha: 0 };
					trail.show = false;
					trail.alpha = 0;
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
	<!-- animated prismatic gradient ribbon (additive light) -->
	<Graphics
		blendMode="add"
		draw={(g) => {
			const s = trail;
			if (!s.show || s.alpha <= 0.01) return;
			const dx = s.headX - s.tailX;
			const dy = s.headY - s.tailY;
			const len = Math.hypot(dx, dy);
			if (len < 3) return;
			const horiz = Math.abs(dx) > Math.abs(dy);
			const N = Math.max(6, Math.min(48, Math.ceil(len / 12)));
			for (let i = 0; i < N; i++) {
				const t0 = i / N;
				const t1 = (i + 1) / N;
				const midT = (t0 + t1) / 2;
				const drainMul = clamp01((midT - s.drain) * 6 + 0.12);
				if (drainMul <= 0.01) continue;
				const w =
					SYMBOL_SIZE *
					(TRAIL_W_TAIL + (TRAIL_W_HEAD - TRAIL_W_TAIL) * EASE.load(midT)) *
					(1 + 0.05 * Math.sin(s.phase * Math.PI * 4 + midT * 9));
				const col = paletteAt(midT * 0.8 - s.phase);
				const a = (0.3 + 0.55 * midT) * s.alpha * drainMul;
				const x0 = s.tailX + dx * t0;
				const y0 = s.tailY + dy * t0;
				const x1 = s.tailX + dx * t1;
				const y1 = s.tailY + dy * t1;
				if (horiz) {
					const xa = Math.min(x0, x1) - 1;
					const wseg = Math.abs(x1 - x0) + 2;
					g.rect(xa, y0 - w * 0.95, wseg, w * 1.9).fill({ color: col, alpha: a * 0.2 });
					g.rect(xa, y0 - w * 0.5, wseg, w).fill({ color: col, alpha: a * 0.72 });
					g.rect(xa, y0 - w * 0.17, wseg, w * 0.34).fill({ color: 0xffffff, alpha: a * 0.8 });
				} else {
					const ya = Math.min(y0, y1) - 1;
					const hseg = Math.abs(y1 - y0) + 2;
					g.rect(x0 - w * 0.95, ya, w * 1.9, hseg).fill({ color: col, alpha: a * 0.2 });
					g.rect(x0 - w * 0.5, ya, w, hseg).fill({ color: col, alpha: a * 0.72 });
					g.rect(x0 - w * 0.17, ya, w * 0.34, hseg).fill({ color: 0xffffff, alpha: a * 0.8 });
				}
			}
			const capT = clamp01(1 - s.drain);
			if (capT > 0.02) {
				const capR = SYMBOL_SIZE * TRAIL_W_HEAD * 0.55;
				g.circle(s.headX, s.headY, capR).fill({ color: paletteAt(0.9 - s.phase), alpha: 0.5 * s.alpha * capT });
				g.circle(s.headX, s.headY, capR * 0.5).fill({ color: 0xffffff, alpha: 0.65 * s.alpha * capT });
			}
			for (let k = 0; k < 7; k++) {
				const u = (0.13 + k * 0.145 + s.phase * 0.55) % 1;
				const drainMul = clamp01((u - s.drain) * 6 + 0.12);
				if (drainMul <= 0.01) continue;
				const wob = Math.sin(s.phase * Math.PI * 3.4 + k * 2.3);
				const px = s.tailX + dx * u + (horiz ? 0 : wob * SYMBOL_SIZE * 0.16);
				const py = s.tailY + dy * u + (horiz ? wob * SYMBOL_SIZE * 0.16 : 0);
				const tw = (Math.sin(s.phase * Math.PI * 6 + k * 2.1) + 1) / 2;
				g.circle(px, py, 1.8 + 1.6 * tw).fill({ color: 0xffffff, alpha: (0.25 + 0.5 * tw) * u * s.alpha * drainMul });
			}
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
