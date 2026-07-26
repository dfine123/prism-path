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
	import { Graphics } from 'pixi-svelte';

	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE, CELL_W, BOARD_DIMENSIONS } from '../game/constants';
	import { stateFx } from '../game/stateFx.svelte';
	import { stateWinPop, MULT_Y } from '../game/stateWinPop.svelte';
	import { EASE, clamp01, lerp, paletteAt, lerpColor } from '../game/motion';

	const context = getContext();
	const board = () => context.stateGame.board;

	// ---- feel tunables ---- (tightened pass: every beat trimmed so the sequence reads
	// snappy without one crude global speed-up — draw quicker, hold shorter, merge sooner)
	const DRAW_MS = 95; // sweep-on (left -> right through the winning cells)
	const HOLD_MS = 275; // streaming hold (symbol breath underneath is trimmed to match)
	const FADE_MS = 80; // release
	const LINE_W = 8; // core line width (px)
	const FLOW_HZ = 1.6; // gradient stream speed while held (flowy)
	const CHUNK = 13; // px per gradient chunk
	const POP_MS = 105; // value pop-in (impact right as the sweep completes)
	const MULT_BEAT_MS = 85; // read beat: value + xN visible together
	const MERGE_MS = 170; // xN collapses in while the value rolls to the full amount
	const PUNCH_MS = 110; // impact punch when the full value lands
	const HOLD_MULT_MS = 530; // longer hold for multiplied lines (pop+beat+merge+punch)

	let line = $state({
		show: false,
		pts: [] as { x: number; y: number }[],
		prog: 0, // 0..1 draw-on progress along the polyline
		alpha: 0,
		phase: 0,
	});
	// the per-line WIN VALUE lives in stateWinPop (rendered by WinValuePop, mounted ABOVE
	// the multiplier-badge layer) — this component only drives it frame-by-frame

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
			// board-rect mask clips it, so it slides out from under the frame into the board);
			// a FULL line (last reel hit) also runs out through the right edge the same way
			const pts = [{ x: -CELL_W * 0.6, y: cells[0].y }, ...cells];
			if (cells.length === positions.length && positions.some((p) => p.reel === BOARD_DIMENSIONS.x - 1)) {
				pts.push({ x: CELL_W * (BOARD_DIMENSIONS.x + 0.6), y: cells[cells.length - 1].y });
			}

			const hasMult = multiplier > 1;
			const holdMs = hasMult ? HOLD_MULT_MS : HOLD_MS;
			const mergeStart = POP_MS + MULT_BEAT_MS; // within the hold phase
			const total = DRAW_MS + holdMs + FADE_MS;
			// scaled-time clock: a click mid-sequence raises stateFx.winSpeed (skip-through)
			let lastT = now();
			let el = 0;

			line = { show: true, pts, prog: 0, alpha: 1, phase: 0 };
			Object.assign(stateWinPop, {
				x: cx,
				y: cy,
				scale: 0,
				alpha: 0,
				multY: MULT_Y,
				multScale: 0,
				multAlpha: 0,
				label: bookEventAmountToCurrencyString(hasMult ? baseAmount : amount),
				multLabel: hasMult ? `×${multiplier}` : '',
			});

			const frame = () => {
				const t = now();
				el += (t - lastT) * stateFx.winSpeed;
				lastT = t;
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
						stateWinPop.scale = EASE.impact(pu);
						stateWinPop.alpha = clamp01(pu * 2.5);
					} else if (!hasMult) {
						stateWinPop.scale = 1 + 0.025 * Math.sin(line.phase * Math.PI * 2.4);
						stateWinPop.alpha = 1;
					}

					if (hasMult) {
						// xN pops just after the value (read order: value, then its multiplier)
						const mpu = clamp01((hu - 90) / POP_MS);
						if (hu < mergeStart) {
							stateWinPop.multScale = EASE.impact(mpu);
							stateWinPop.multAlpha = clamp01(mpu * 2.5);
						} else if (hu < mergeStart + MERGE_MS) {
							// MERGE: xN collapses INTO the number while it rolls to the full value
							const mu = clamp01((hu - mergeStart) / MERGE_MS);
							stateWinPop.multY = MULT_Y * (1 - EASE.load(mu));
							stateWinPop.multScale = 1 - 0.7 * mu;
							stateWinPop.multAlpha = 1 - EASE.collapse(mu);
							stateWinPop.label = bookEventAmountToCurrencyString(
								Math.round(lerp(baseAmount, amount, EASE.settle(mu))),
							);
						} else {
							// PUNCH: the full value lands with an impact beat, then breathes
							stateWinPop.multAlpha = 0;
							stateWinPop.label = bookEventAmountToCurrencyString(amount);
							const qu = clamp01((hu - mergeStart - MERGE_MS) / PUNCH_MS);
							stateWinPop.scale =
								qu < 1
									? 1 + 0.24 * Math.sin(Math.PI * qu)
									: 1 + 0.025 * Math.sin(line.phase * Math.PI * 2.4);
							stateWinPop.alpha = 1;
						}
					}
				} else {
					line.prog = 1;
					const fu = clamp01((el - DRAW_MS - holdMs) / FADE_MS);
					line.alpha = 1 - EASE.collapse(fu);
					stateWinPop.alpha = line.alpha;
					stateWinPop.scale = 1 - 0.08 * fu;
					stateWinPop.multAlpha = 0;
				}
				if (el < total) {
					requestAnimationFrame(frame);
				} else {
					line.show = false;
					line.alpha = 0;
					stateWinPop.alpha = 0;
					stateWinPop.scale = 0;
					stateWinPop.multAlpha = 0;
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

			// stroke a chunk FOLLOWING the polyline (corner-correct: pass through any vertex
			// that falls inside [L0, L1] instead of shortcutting across the elbow)
			const strokeSeg = (L0: number, L1: number) => {
				const a = pointAtLen(L0);
				g.moveTo(a.x, a.y);
				for (let i = 1; i < pts.length; i++) {
					if (cum[i] > L0 && cum[i] < L1) g.lineTo(pts[i].x, pts[i].y);
				}
				const b = pointAtLen(L1);
				g.lineTo(b.x, b.y);
			};

			// gradient ribbon — the LINE ITSELF is the luminescent gradient: streaming prism
			// hues + a traveling white-hot shimmer band. BUTT caps (not round) so the chunks
			// fuse into one continuous ribbon instead of reading as a chain of circles.
			const nChunks = Math.max(3, Math.ceil(drawnLen / CHUNK));
			for (let i = 0; i < nChunks; i++) {
				const L0 = (drawnLen * i) / nChunks;
				const L1 = Math.min((drawnLen * (i + 1)) / nChunks + 1.5, drawnLen); // overlap kills seams
				const u = (L0 + L1) / 2 / totalLen;
				const col = paletteAt(u * 0.8 - s.phase);
				const shimmer = clamp01(0.5 + 0.5 * Math.sin(Math.PI * 2 * (u * 1.5 - s.phase * 1.5)));
				const coreCol = lerpColor(col, 0xffffff, 0.35 + 0.5 * shimmer);
				strokeSeg(L0, L1);
				g.stroke({ width: LINE_W * 2.4, color: col, alpha: 0.16 * s.alpha, cap: 'butt', join: 'round' });
				strokeSeg(L0, L1);
				g.stroke({ width: LINE_W * 1.05, color: col, alpha: 0.85 * s.alpha, cap: 'butt', join: 'round' });
				strokeSeg(L0, L1);
				g.stroke({
					width: LINE_W * (0.34 + 0.14 * shimmer),
					color: coreCol,
					alpha: (0.5 + 0.4 * shimmer) * s.alpha,
					cap: 'butt',
					join: 'round',
				});
			}

			// 4-point crystal star glint (the game's sparkle language, not a plain circle)
			const glint = (x: number, y: number, r: number, col: number, a: number) => {
				g.moveTo(x - r, y).lineTo(x + r, y).stroke({ width: 1.6, color: col, alpha: a, cap: 'round' });
				g.moveTo(x, y - r).lineTo(x, y + r).stroke({ width: 1.6, color: col, alpha: a, cap: 'round' });
				g.circle(x, y, Math.max(1.2, r * 0.3)).fill({ color: 0xffffff, alpha: a });
			};

			if (s.prog < 1) {
				// comet head: a direction-aligned teardrop with a star glint at its tip
				const h = pointAtLen(drawnLen);
				const back = pointAtLen(Math.max(0, drawnLen - 8));
				let dx = h.x - back.x;
				let dy = h.y - back.y;
				const dl = Math.hypot(dx, dy) || 1;
				dx /= dl;
				dy /= dl;
				const px = -dy;
				const py = dx;
				const W2 = LINE_W * 0.95;
				g.poly([
					{ x: h.x + dx * 5, y: h.y + dy * 5 }, // tip
					{ x: h.x - dx * 4 + px * W2, y: h.y - dy * 4 + py * W2 },
					{ x: h.x - dx * 14, y: h.y - dy * 14 }, // tail
					{ x: h.x - dx * 4 - px * W2, y: h.y - dy * 4 - py * W2 },
				]).fill({ color: 0xffffff, alpha: 0.8 * s.alpha });
				g.circle(h.x, h.y, LINE_W * 2.2).fill({ color: paletteAt(-s.phase), alpha: 0.22 * s.alpha });
				glint(h.x + dx * 5, h.y + dy * 5, LINE_W * 1.4, 0xffffff, 0.9 * s.alpha);
			} else {
				// held: terminal glint at the line's end + tiny twinkles drifting along it
				const e = pointAtLen(drawnLen);
				glint(e.x, e.y, LINE_W * 1.1, 0xffffff, 0.55 * s.alpha);
				for (let k = 0; k < 3; k++) {
					const u = ((k * 0.317 + s.phase * 0.23) % 1 + 1) % 1;
					const p = pointAtLen(u * drawnLen);
					const tw = (Math.sin(s.phase * Math.PI * 3 + k * 2.1) + 1) / 2;
					glint(p.x, p.y, 3 + 4 * tw, lerpColor(paletteAt(u - s.phase), 0xffffff, 0.6), (0.25 + 0.5 * tw) * s.alpha);
				}
			}
		}}
	/>

{/if}
