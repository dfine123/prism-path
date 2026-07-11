<script lang="ts" module>
	import type { Position } from '../game/types';

	// Awaitable win-line presentation: sweeps a prism-light line through the winning cells,
	// pops the line's WIN VALUE at the centroid on the impact frame, holds while streaming,
	// then fades. The winInfo handler awaits one full lifecycle per line, so lines play
	// strictly sequentially.
	export type EmitterEventWinLines = { type: 'winLinePlay'; positions: Position[]; label: string };
</script>

<script lang="ts">
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { EASE, clamp01, lerp, paletteAt, lerpColor } from '../game/motion';

	const context = getContext();
	const board = () => context.stateGame.board;

	// ---- feel tunables ----
	const DRAW_MS = 260; // sweep-on (left -> right through the winning cells)
	const HOLD_MS = 620; // streaming hold (matches the symbol breath underneath)
	const FADE_MS = 150; // release
	const LINE_W = 11; // core line width (px)
	const FLOW_HZ = 0.8; // gradient stream speed while held
	const CHUNK = 13; // px per gradient chunk
	const POP_MS = 170; // value plaque pop-in (impact right as the sweep completes)
	const POP_FONT = 36;

	let line = $state({
		show: false,
		pts: [] as { x: number; y: number }[],
		prog: 0, // 0..1 draw-on progress along the polyline
		alpha: 0,
		phase: 0,
	});
	// the per-line WIN VALUE plaque (standard slots pattern: value pops at the line's centre)
	let pop = $state({ x: 0, y: 0, scale: 0, alpha: 0, textW: 0, textH: 0 });
	let label = $state('');

	const now = () => performance.now();

	const cellPos = (p: Position) => {
		const sym = board()[p.reel]?.reelState?.symbols?.[p.row];
		const y = sym && typeof sym.symbolY === 'function' ? sym.symbolY() : (p.row - 0.5) * SYMBOL_SIZE;
		return { x: getSymbolX(p.reel), y };
	};

	const play = (positions: Position[], winLabel: string) =>
		new Promise<void>((resolve) => {
			const cells = [...positions].sort((a, b) => a.reel - b.reel).map(cellPos);
			if (cells.length === 0) return resolve();
			// the value plaque sits at the centroid of the WINNING cells (before the edge anchor)
			const cx = cells.reduce((s, p) => s + p.x, 0) / cells.length;
			const cy = cells.reduce((s, p) => s + p.y, 0) / cells.length;
			// paylines read left-to-right: launch the line FROM the board's left edge (tucked
			// just under the frame) into the first winning symbol
			const pts = [{ x: -SYMBOL_SIZE * 0.04, y: cells[0].y }, ...cells];
			const start = now();
			const total = DRAW_MS + HOLD_MS + FADE_MS;
			line = { show: true, pts, prog: 0, alpha: 1, phase: 0 };
			label = winLabel;
			pop = { x: cx, y: cy, scale: 0, alpha: 0, textW: pop.textW, textH: pop.textH };

			const frame = () => {
				const el = now() - start;
				line.phase = (el / 1000) * FLOW_HZ;
				if (el < DRAW_MS) {
					line.prog = EASE.settle(clamp01(el / DRAW_MS));
					line.alpha = 1;
				} else if (el < DRAW_MS + HOLD_MS) {
					line.prog = 1;
					line.alpha = 1;
					// value plaque: IMPACT pop as the sweep completes, then a gentle breathe
					const pu = clamp01((el - DRAW_MS) / POP_MS);
					if (pu < 1) {
						pop.scale = EASE.impact(pu);
						pop.alpha = clamp01(pu * 2.5);
					} else {
						pop.scale = 1 + 0.025 * Math.sin(line.phase * Math.PI * 2.4);
						pop.alpha = 1;
					}
				} else {
					line.prog = 1;
					const fu = clamp01((el - DRAW_MS - HOLD_MS) / FADE_MS);
					line.alpha = 1 - EASE.collapse(fu);
					pop.alpha = line.alpha;
					pop.scale = 1 - 0.08 * fu;
				}
				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					line.show = false;
					line.alpha = 0;
					pop.alpha = 0;
					pop.scale = 0;
					resolve();
				}
			};
			requestAnimationFrame(frame);
		});

	context.eventEmitter.subscribeOnMount({
		winLinePlay: async ({ positions, label: winLabel }) => {
			await play(positions, winLabel);
		},
	});
</script>

{#if line.show}
	<!-- contrast plate: near-black outline UNDER the light (normal blend — additive black is
	     invisible), so the gradient line pops against the grey board and bright symbols -->
	<Graphics
		draw={(g) => {
			const s = line;
			if (!s.show || s.alpha <= 0.01 || s.pts.length === 0) return;
			const pts = s.pts;
			const cum = [0];
			for (let i = 1; i < pts.length; i++) {
				cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
			}
			const totalLen = Math.max(cum[cum.length - 1], 1);
			const drawnLen = totalLen * s.prog;
			g.moveTo(pts[0].x, pts[0].y);
			let end = pts[pts.length - 1];
			for (let i = 1; i < pts.length; i++) {
				if (cum[i] <= drawnLen) {
					g.lineTo(pts[i].x, pts[i].y);
				} else {
					const t = clamp01((drawnLen - cum[i - 1]) / Math.max(cum[i] - cum[i - 1], 0.001));
					end = { x: lerp(pts[i - 1].x, pts[i].x, t), y: lerp(pts[i - 1].y, pts[i].y, t) };
					g.lineTo(end.x, end.y);
					break;
				}
			}
			// soft feathered edge + solid outline
			g.stroke({ width: LINE_W * 2.5, color: 0x0b0814, alpha: 0.5 * s.alpha, cap: 'round', join: 'round' });
			g.moveTo(pts[0].x, pts[0].y);
			for (let i = 1; i < pts.length; i++) {
				if (cum[i] <= drawnLen) g.lineTo(pts[i].x, pts[i].y);
				else {
					g.lineTo(end.x, end.y);
					break;
				}
			}
			g.stroke({ width: LINE_W * 1.8, color: 0x0b0814, alpha: 0.92 * s.alpha, cap: 'round', join: 'round' });
		}}
	/>
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

			// gradient chunks — the LINE ITSELF is the luminescent gradient: streaming prism hues
			// as the base, and a traveling white-hot shimmer band instead of a flat white core.
			const nChunks = Math.max(3, Math.ceil(drawnLen / CHUNK));
			for (let i = 0; i < nChunks; i++) {
				const L0 = (drawnLen * i) / nChunks;
				const L1 = (drawnLen * (i + 1)) / nChunks;
				const a = pointAtLen(L0);
				const b = pointAtLen(L1 + 0.75); // slight overlap kills seams
				const u = (L0 + L1) / 2 / totalLen;
				const col = paletteAt(u * 0.8 - s.phase);
				// shimmer: a bright pulse that sweeps along the line while it holds
				const shimmer = clamp01(0.5 + 0.5 * Math.sin(Math.PI * 2 * (u * 1.5 - s.phase * 1.5)));
				const coreCol = lerpColor(col, 0xffffff, 0.35 + 0.5 * shimmer);
				g.moveTo(a.x, a.y).lineTo(b.x, b.y).stroke({ width: LINE_W * 2.6, color: col, alpha: 0.2 * s.alpha, cap: 'round' });
				g.moveTo(a.x, a.y).lineTo(b.x, b.y).stroke({ width: LINE_W * 1.05, color: col, alpha: 0.85 * s.alpha, cap: 'round' });
				g.moveTo(a.x, a.y).lineTo(b.x, b.y).stroke({
					width: LINE_W * (0.34 + 0.14 * shimmer),
					color: coreCol,
					alpha: (0.5 + 0.4 * shimmer) * s.alpha,
					cap: 'round',
				});
			}

			// sweep head spark while drawing on (the line + symbol breath carry the rest)
			if (s.prog < 1) {
				const h = pointAtLen(drawnLen);
				g.circle(h.x, h.y, LINE_W * 1.5).fill({ color: 0xffffff, alpha: 0.85 * s.alpha });
				g.circle(h.x, h.y, LINE_W * 2.6).fill({ color: paletteAt(-s.phase), alpha: 0.3 * s.alpha });
			}
		}}
	/>

	<!-- the line's WIN VALUE: pops at the centroid on the sweep's impact frame -->
	{#if pop.alpha > 0.01}
		<Container x={pop.x} y={pop.y} scale={pop.scale} alpha={pop.alpha}>
			<Graphics
				draw={(g) => {
					const w = pop.textW + 30;
					const h = pop.textH + 14;
					g.roundRect(-w / 2, -h / 2, w, h, 12).fill({ color: 0x0b0814, alpha: 0.88 });
					g.roundRect(-w / 2, -h / 2, w, h, 12).stroke({ width: 2, color: 0xffffff, alpha: 0.85 });
				}}
			/>
			<BitmapText
				anchor={0.5}
				text={label}
				style={prismStyle(POP_FONT)}
				onresize={(sizes) => {
					pop.textW = sizes.width;
					pop.textH = sizes.height;
				}}
			/>
		</Container>
	{/if}
{/if}
