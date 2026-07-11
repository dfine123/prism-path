<script lang="ts" module>
	import type { Position } from '../game/types';

	// Awaitable win-line presentation: sweeps a prism-light line through the winning cells
	// (joint pulse as it passes each one), holds while streaming, then fades. The winInfo
	// handler awaits one full lifecycle per line, so lines play strictly sequentially.
	export type EmitterEventWinLines = { type: 'winLinePlay'; positions: Position[] };
</script>

<script lang="ts">
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import { EASE, clamp01, lerp, paletteAt } from '../game/motion';

	const context = getContext();
	const board = () => context.stateGame.board;

	// ---- feel tunables ----
	const DRAW_MS = 260; // sweep-on (left -> right through the winning cells)
	const HOLD_MS = 620; // streaming hold (matches the symbol breath underneath)
	const FADE_MS = 150; // release
	const LINE_W = 11; // core line width (px)
	const FLOW_HZ = 0.8; // gradient stream speed while held
	const CHUNK = 13; // px per gradient chunk

	let line = $state({
		show: false,
		pts: [] as { x: number; y: number }[],
		prog: 0, // 0..1 draw-on progress along the polyline
		alpha: 0,
		phase: 0,
	});

	const now = () => performance.now();

	const cellPos = (p: Position) => {
		const sym = board()[p.reel]?.reelState?.symbols?.[p.row];
		const y = sym && typeof sym.symbolY === 'function' ? sym.symbolY() : (p.row - 0.5) * SYMBOL_SIZE;
		return { x: getSymbolX(p.reel), y };
	};

	const play = (positions: Position[]) =>
		new Promise<void>((resolve) => {
			const pts = [...positions]
				.sort((a, b) => a.reel - b.reel)
				.map(cellPos);
			if (pts.length === 0) return resolve();
			const start = now();
			const total = DRAW_MS + HOLD_MS + FADE_MS;
			line = { show: true, pts, prog: 0, alpha: 1, phase: 0 };

			const frame = () => {
				const el = now() - start;
				line.phase = (el / 1000) * FLOW_HZ;
				if (el < DRAW_MS) {
					line.prog = EASE.settle(clamp01(el / DRAW_MS));
					line.alpha = 1;
				} else if (el < DRAW_MS + HOLD_MS) {
					line.prog = 1;
					line.alpha = 1;
				} else {
					line.prog = 1;
					line.alpha = 1 - EASE.collapse(clamp01((el - DRAW_MS - HOLD_MS) / FADE_MS));
				}
				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					line.show = false;
					line.alpha = 0;
					resolve();
				}
			};
			requestAnimationFrame(frame);
		});

	context.eventEmitter.subscribeOnMount({
		winLinePlay: async ({ positions }) => {
			await play(positions);
		},
	});
</script>

{#if line.show}
	<Graphics
		blendMode="add"
		draw={(g) => {
			const s = line;
			if (!s.show || s.alpha <= 0.01 || s.pts.length === 0) return;
			const pts = s.pts;
			// cumulative lengths along the polyline
			const cum = [0];
			for (let i = 1; i < pts.length; i++) {
				cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
			}
			const totalLen = Math.max(cum[cum.length - 1], 1);
			const drawnLen = totalLen * s.prog;

			const pointAtLen = (L: number) => {
				for (let i = 1; i < pts.length; i++) {
					if (L <= cum[i] || i === pts.length - 1) {
						const t = clamp01((L - cum[i - 1]) / Math.max(cum[i] - cum[i - 1], 0.001));
						return { x: lerp(pts[i - 1].x, pts[i].x, t), y: lerp(pts[i - 1].y, pts[i].y, t) };
					}
				}
				return pts[pts.length - 1];
			};

			// gradient chunks: glow / body / hot core, hues streaming along the drawn length
			const nChunks = Math.max(3, Math.ceil(drawnLen / CHUNK));
			for (let i = 0; i < nChunks; i++) {
				const L0 = (drawnLen * i) / nChunks;
				const L1 = (drawnLen * (i + 1)) / nChunks;
				const a = pointAtLen(L0);
				const b = pointAtLen(L1 + 0.75); // slight overlap kills seams
				const u = (L0 + L1) / 2 / totalLen;
				const col = paletteAt(u * 0.8 - s.phase);
				g.moveTo(a.x, a.y).lineTo(b.x, b.y).stroke({ width: LINE_W * 2.4, color: col, alpha: 0.16 * s.alpha, cap: 'round' });
				g.moveTo(a.x, a.y).lineTo(b.x, b.y).stroke({ width: LINE_W, color: col, alpha: 0.75 * s.alpha, cap: 'round' });
				g.moveTo(a.x, a.y).lineTo(b.x, b.y).stroke({ width: LINE_W * 0.36, color: 0xffffff, alpha: 0.85 * s.alpha, cap: 'round' });
			}

			// sweep head spark while drawing on
			if (s.prog < 1) {
				const h = pointAtLen(drawnLen);
				g.circle(h.x, h.y, LINE_W * 1.5).fill({ color: 0xffffff, alpha: 0.85 * s.alpha });
				g.circle(h.x, h.y, LINE_W * 2.6).fill({ color: paletteAt(-s.phase), alpha: 0.3 * s.alpha });
			}

			// joint pulse at each winning cell: rings bloom as the sweep passes, then breathe
			for (let i = 0; i < pts.length; i++) {
				const reached = clamp01((drawnLen - cum[i]) / (SYMBOL_SIZE * 0.5) + 1);
				if (reached <= 0.02) continue;
				const bloom = EASE.impact(clamp01(reached));
				const breathe = 1 + 0.07 * Math.sin(s.phase * Math.PI * 2 + i * 0.9);
				const r = SYMBOL_SIZE * 0.46 * bloom * breathe;
				const col = paletteAt(i / Math.max(pts.length - 1, 1) * 0.8 - s.phase);
				g.circle(pts[i].x, pts[i].y, r).stroke({ width: 3.5, color: col, alpha: 0.55 * s.alpha });
				g.circle(pts[i].x, pts[i].y, r * 0.82).stroke({ width: 1.5, color: 0xffffff, alpha: 0.35 * s.alpha });
			}
		}}
	/>
{/if}
