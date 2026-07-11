<script lang="ts" module>
	import type { Position } from '../game/types';

	// Awaitable win-line presentation: sweeps a prism-light line through the winning cells,
	// pops the line's WIN VALUE at the centroid on the impact frame (with its beast multiplier,
	// which collapses into the number as it rolls up to the full value), holds while streaming,
	// then fades. The winInfo handler awaits one full lifecycle per line, so lines play
	// strictly sequentially.
	export type EmitterEventWinLines = {
		type: 'winLinePlay';
		positions: Position[];
		amount: number; // final line win (multiplier applied)
		baseAmount: number; // line win before the beast multiplier
		multiplier: number; // product of distinct beasts on the line (1 = none)
	};
</script>

<script lang="ts">
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { prismStyle } from '../game/fonts';
	import { EASE, clamp01, lerp, paletteAt, lerpColor } from '../game/motion';

	const context = getContext();
	const board = () => context.stateGame.board;

	// ---- feel tunables ----
	const DRAW_MS = 135; // sweep-on (left -> right through the winning cells)
	const HOLD_MS = 360; // streaming hold (matches the symbol breath underneath)
	const FADE_MS = 95; // release
	const LINE_W = 11; // core line width (px)
	const FLOW_HZ = 1.45; // gradient stream speed while held (flowy)
	const CHUNK = 13; // px per gradient chunk
	const POP_MS = 125; // value pop-in (impact right as the sweep completes)
	const POP_FONT = 40;
	const MULT_FONT = 32;
	const MULT_Y = 40; // the xN sits under the value before merging into it
	const MULT_BEAT_MS = 110; // read beat: value + xN visible together
	const MERGE_MS = 210; // xN collapses in while the value rolls to the full amount
	const PUNCH_MS = 130; // impact punch when the full value lands
	const HOLD_MULT_MS = 640; // longer hold for multiplied lines (pop+beat+merge+punch)

	let line = $state({
		show: false,
		pts: [] as { x: number; y: number }[],
		prog: 0, // 0..1 draw-on progress along the polyline
		alpha: 0,
		phase: 0,
	});
	// the per-line WIN VALUE (standard slots pattern: value pops at the line's centre; a beast
	// multiplier pops with it, then collapses into the number as it rolls to the full value)
	let pop = $state({ x: 0, y: 0, scale: 0, alpha: 0 });
	let multFx = $state({ y: MULT_Y, scale: 0, alpha: 0 });
	let label = $state('');
	let multLabel = $state('');

	const now = () => performance.now();

	const cellPos = (p: Position) => {
		const sym = board()[p.reel]?.reelState?.symbols?.[p.row];
		const y = sym && typeof sym.symbolY === 'function' ? sym.symbolY() : (p.row - 0.5) * SYMBOL_SIZE;
		return { x: getSymbolX(p.reel), y };
	};

	const play = (positions: Position[], amount: number, baseAmount: number, multiplier: number) =>
		new Promise<void>((resolve) => {
			const cells = [...positions].sort((a, b) => a.reel - b.reel).map(cellPos);
			if (cells.length === 0) return resolve();
			// the value sits at the centroid of the WINNING cells (before the edge anchor)
			const cx = cells.reduce((s, p) => s + p.x, 0) / cells.length;
			const cy = cells.reduce((s, p) => s + p.y, 0) / cells.length;
			// paylines read left-to-right: the line launches from BEHIND the frame border (the
			// board-rect mask clips it, so it slides out from under the frame into the board)
			const pts = [{ x: -CELL_W * 0.6, y: cells[0].y }, ...cells];

			const hasMult = multiplier > 1;
			const holdMs = hasMult ? HOLD_MULT_MS : HOLD_MS;
			const mergeStart = POP_MS + MULT_BEAT_MS; // within the hold phase
			const start = now();
			const total = DRAW_MS + holdMs + FADE_MS;

			line = { show: true, pts, prog: 0, alpha: 1, phase: 0 };
			label = bookEventAmountToCurrencyString(hasMult ? baseAmount : amount);
			multLabel = hasMult ? `×${multiplier}` : '';
			pop = { x: cx, y: cy, scale: 0, alpha: 0 };
			multFx = { y: MULT_Y, scale: 0, alpha: 0 };

			const frame = () => {
				const el = now() - start;
				line.phase = (el / 1000) * FLOW_HZ;
				if (el < DRAW_MS) {
					// glide (cubicOut): continuous fluid sweep, no expo snap-then-crawl
					line.prog = EASE.glide(clamp01(el / DRAW_MS));
					line.alpha = 1;
				} else if (el < DRAW_MS + holdMs) {
					line.prog = 1;
					line.alpha = 1;
					const hu = el - DRAW_MS;

					// value: IMPACT pop as the sweep completes
					const pu = clamp01(hu / POP_MS);
					if (pu < 1) {
						pop.scale = EASE.impact(pu);
						pop.alpha = clamp01(pu * 2.5);
					} else if (!hasMult) {
						pop.scale = 1 + 0.025 * Math.sin(line.phase * Math.PI * 2.4);
						pop.alpha = 1;
					}

					if (hasMult) {
						// xN pops just after the value (read order: value, then its multiplier)
						const mpu = clamp01((hu - 90) / POP_MS);
						if (hu < mergeStart) {
							multFx.scale = EASE.impact(mpu);
							multFx.alpha = clamp01(mpu * 2.5);
						} else if (hu < mergeStart + MERGE_MS) {
							// MERGE: xN collapses INTO the number while it rolls to the full value
							const mu = clamp01((hu - mergeStart) / MERGE_MS);
							multFx.y = MULT_Y * (1 - EASE.load(mu));
							multFx.scale = 1 - 0.7 * mu;
							multFx.alpha = 1 - EASE.collapse(mu);
							label = bookEventAmountToCurrencyString(
								Math.round(lerp(baseAmount, amount, EASE.settle(mu))),
							);
						} else {
							// PUNCH: the full value lands with an impact beat, then breathes
							multFx.alpha = 0;
							label = bookEventAmountToCurrencyString(amount);
							const qu = clamp01((hu - mergeStart - MERGE_MS) / PUNCH_MS);
							pop.scale =
								qu < 1
									? 1 + 0.24 * Math.sin(Math.PI * qu)
									: 1 + 0.025 * Math.sin(line.phase * Math.PI * 2.4);
							pop.alpha = 1;
						}
					}
				} else {
					line.prog = 1;
					const fu = clamp01((el - DRAW_MS - holdMs) / FADE_MS);
					line.alpha = 1 - EASE.collapse(fu);
					pop.alpha = line.alpha;
					pop.scale = 1 - 0.08 * fu;
					multFx.alpha = 0;
				}
				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					line.show = false;
					line.alpha = 0;
					pop.alpha = 0;
					pop.scale = 0;
					multFx.alpha = 0;
					resolve();
				}
			};
			requestAnimationFrame(frame);
		});

	context.eventEmitter.subscribeOnMount({
		winLinePlay: async ({ positions, amount, baseAmount, multiplier }) => {
			await play(positions, amount, baseAmount, multiplier);
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

	<!-- the line's WIN VALUE: bare number pops at the centroid on the sweep's impact frame;
	     its beast multiplier pops beneath, then collapses in as the value rolls to the total -->
	{#if pop.alpha > 0.01}
		<Container x={pop.x} y={pop.y} scale={pop.scale} alpha={pop.alpha}>
			<BitmapText anchor={0.5} text={label} style={prismStyle(POP_FONT)} />
			{#if multLabel && multFx.alpha > 0.01}
				<Container y={multFx.y} scale={multFx.scale} alpha={multFx.alpha}>
					<BitmapText anchor={0.5} text={multLabel} style={prismStyle(MULT_FONT)} />
				</Container>
			{/if}
		</Container>
	{/if}
{/if}
