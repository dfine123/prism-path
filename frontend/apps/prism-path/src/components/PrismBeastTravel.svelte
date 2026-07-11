<script lang="ts" module>
	import type { Position } from '../game/types';

	// The Prism Beast travel overlay. Per dragon the math emits prismBeast (land/charge) then
	// prismPath (the fired path). This overlay owns the *feel*:
	//   NON-STICKY — the dragon winds up, PUSHES off with a squash-stretch, FLOWS along the
	//   path streaming a prismatic gradient ribbon, converts each covered cell to a trail
	//   wild, and pushes fully OFF the board while the ribbon drains after it.
	//   STICKY — the dragon STAYS SEATED on its cell: it winds up, LUNGES toward its firing
	//   direction while the light ribbon shoots the path (revealing trail wilds), then
	//   settles back onto its seat with its multiplier badge. Next spin it fires again.
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
	import { SYMBOL_SIZE } from '../game/constants';
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
	const WINDUP_MS = 120; // anticipation: a coiled charge IN PLACE (no pull-back — pure push)
	const PER_CELL_MS = 78; // flow speed
	const TRAVEL_MIN_MS = 175;
	const BURST_MS = 400; // head pushes off the edge; ribbon holds the line then drains
	const STRETCH = 0.6; // squash-stretch amount at peak flow (the "push")
	const EXIT_PUSH = 1.5; // head flies fully OFF the board on the burst (x symbol)
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
	// Stickiness is signalled by the glowing square marker (StickyDragonMarkers), not the cell.
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
		context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
	};

	const runTravel = (beast: BeastTravel) =>
		new Promise<void>((resolve) => {
			const dir = beast.direction;
			asset = BEAST_ASSET[dir] ?? 'beastDown';
			const dv = DIRV[dir];
			const horizontal = dv.x !== 0;
			const origin = cellPos(beast.origin);
			// EVERY dragon (sticky included) plays the same full travel — the route includes its
			// own cell (cells[0]); stickiness is signalled by the glowing square marker instead.
			const pts = beast.cells.length > 0 ? beast.cells.map((c) => cellPos(c.position)) : [origin];
			const N = pts.length;
			const travelMs = Math.max(TRAVEL_MIN_MS, PER_CELL_MS * Math.max(1, N - 1));
			const total = WINDUP_MS + travelMs + BURST_MS;
			const start = now();
			const revealed = new Set<number>();

			visible = true;
			dragon = { x: origin.x, y: origin.y, sx: DRAGON_SCALE, sy: DRAGON_SCALE, alpha: 0 };
			glowAlpha = 0;
			flash = { x: origin.x, y: origin.y, r: 0, alpha: 0 };
			trail = { show: false, tailX: origin.x, tailY: origin.y, headX: origin.x, headY: origin.y, phase: 0, alpha: 0, drain: 0 };

			const posAt = (p: number) => {
				if (N <= 1) return { x: origin.x + dv.x * p * SYMBOL_SIZE * 0.6, y: origin.y + dv.y * p * SYMBOL_SIZE * 0.6 };
				const f = clamp01(p) * (N - 1);
				const i = Math.min(N - 2, Math.floor(f));
				const t = f - i;
				return { x: lerp(pts[i].x, pts[i + 1].x, t), y: lerp(pts[i].y, pts[i + 1].y, t) };
			};

			const applyStretch = (amt: number) => {
				const along = 1 + amt;
				const perp = 1 - 0.45 * amt;
				dragon.sx = DRAGON_SCALE * (horizontal ? along : perp);
				dragon.sy = DRAGON_SCALE * (horizontal ? perp : along);
			};

			const revealUpTo = (idx: number) => {
				for (let i = 0; i <= Math.min(idx, beast.cells.length - 1); i++) {
					if (revealed.has(i)) continue;
					revealed.add(i);
					const c = beast.cells[i];
					revealCell(c.position.reel, c.position.row, dir, c.multiplier);
				}
			};

			const frame = () => {
				const el = now() - start;
				trail.phase = (el / 1000) * TRAIL_FLOW_HZ;

				if (el < WINDUP_MS) {
					// ANTICIPATION — a coiled charge IN PLACE: fade in + compress along the fire
					// axis (loading the spring), then everything releases FORWARD. No pull-back.
					const wp = EASE.load(clamp01(el / WINDUP_MS));
					dragon.alpha = wp;
					dragon.x = origin.x;
					dragon.y = origin.y;
					applyStretch(-0.16 * wp);
					glowAlpha = 0.5 * wp;
				} else if (el < WINDUP_MS + travelMs) {
					// PUSH + FLOW — launch along the path, gradient ribbon streaming behind.
					const elFlow = el - WINDUP_MS;
					const tp = clamp01(elFlow / travelMs);
					const p = EASE.glide(tp);
					const pos = posAt(p);
					dragon.x = pos.x;
					dragon.y = pos.y;
					dragon.alpha = 1;
					applyStretch(STRETCH * Math.sin(Math.PI * tp));
					glowAlpha = 0.85;
					trail.show = true;
					trail.alpha = clamp01(elFlow / 90);
					trail.headX = pos.x - dv.x * TRAIL_TUCK * SYMBOL_SIZE;
					trail.headY = pos.y - dv.y * TRAIL_TUCK * SYMBOL_SIZE;
					revealUpTo(Math.floor(p * Math.max(N - 1, 1) + 0.001));
				} else {
					// BURST — the head pushes fully OFF the board; the ribbon holds the completed
					// wild line, then DRAINS tail-first after the dragon; ring flash at the edge.
					const bp = clamp01((el - WINDUP_MS - travelMs) / BURST_MS);
					const edge = posAt(1);
					const ee = EASE.settle(bp);
					dragon.x = edge.x + dv.x * EXIT_PUSH * SYMBOL_SIZE * ee;
					dragon.y = edge.y + dv.y * EXIT_PUSH * SYMBOL_SIZE * ee;
					dragon.alpha = 1 - EASE.collapse(clamp01(bp / 0.7));
					applyStretch(STRETCH * (1 - bp));
					glowAlpha = 0.85 * (1 - EASE.collapse(clamp01(bp / 0.7)));
					trail.headX = edge.x + dv.x * 0.18 * SYMBOL_SIZE;
					trail.headY = edge.y + dv.y * 0.18 * SYMBOL_SIZE;
					trail.drain = EASE.collapse(clamp01((bp - 0.3) / 0.7));
					trail.alpha = 1 - EASE.collapse(clamp01((bp - 0.45) / 0.55));
					flash = {
						x: edge.x,
						y: edge.y,
						r: EASE.impact(clamp01(bp / 0.6)) * SYMBOL_SIZE * 1.15,
						alpha: (1 - clamp01(bp / 0.6)) * 0.85,
					};
					revealUpTo(N - 1);
				}

				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					// safety: every cell resolved before handing back control
					revealUpTo(beast.cells.length - 1);
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
