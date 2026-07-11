// THE trail-beam renderer — single source for the prism wild-path light. Used by BOTH the
// dragon's in-flight ribbon (PrismBeastTravel) and the persistent trail cells
// (WildTrailSymbol), so the hand-off between "path animating behind the dragon" and "the
// path itself" is pixel-identical: same clock, same gradient space (wraps once per cell —
// tiles seamlessly across a line), same widths/alphas/motes. Never diverge these two.
import type * as PIXI from 'pixi.js';

import { CELL_W, SYMBOL_SIZE } from './constants';
import { paletteAt } from './motion';

export const TRAIL_FLOW_HZ = 0.55; // stream speed (phase = seconds * this, absolute clock)
export const TRAIL_HOT_FLIGHT = 1.35; // flight heat; cells settle in FROM this value
const W_BASE = 0.44;
const SEGS = 6;

export type TrailBeamOpts = {
	cx: number; // beam centre (board/cell-local coords)
	cy: number;
	horizontal: boolean;
	flowSign: number; // -1 for left/up, +1 for right/down (gradient streams in fire direction)
	phase: number;
	hot: number; // 1 = resting; TRAIL_HOT_FLIGHT while firing / settle-in start
	clipFrom?: number; // local coords along the axis (default: full cell)
	clipTo?: number;
};

export const drawTrailBeam = (g: PIXI.Graphics, o: TrailBeamOpts) => {
	const L = o.horizontal ? CELL_W : SYMBOL_SIZE;
	const lo = o.clipFrom ?? -L / 2;
	const hi = o.clipTo ?? L / 2;
	if (hi - lo < 1) return;
	const breathe = 0.92 + 0.08 * Math.sin(o.phase * Math.PI * 1.6);
	const aMul = breathe * o.hot;
	const W = SYMBOL_SIZE * W_BASE * (1 + (o.hot - 1) * 0.35);
	for (let i = 0; i < SEGS; i++) {
		const u0 = i / SEGS;
		const u1 = (i + 1) / SEGS;
		let p0 = -L / 2 + u0 * L;
		let p1 = -L / 2 + u1 * L;
		if (p1 < lo || p0 > hi) continue;
		p0 = Math.max(p0, lo);
		p1 = Math.min(p1, hi);
		const mid = (u0 + u1) / 2;
		const col = paletteAt(o.flowSign * mid - o.phase);
		const w = W * (1 + 0.06 * Math.sin((o.flowSign * mid - o.phase) * Math.PI * 2));
		const seg = p1 - p0 + 1;
		if (o.horizontal) {
			g.rect(o.cx + p0 - 0.5, o.cy - w * 0.9, seg, w * 1.8).fill({ color: col, alpha: 0.1 * aMul });
			g.rect(o.cx + p0 - 0.5, o.cy - w * 0.5, seg, w).fill({ color: col, alpha: 0.32 * aMul });
			g.rect(o.cx + p0 - 0.5, o.cy - w * 0.16, seg, w * 0.32).fill({ color: 0xffffff, alpha: 0.3 * aMul });
		} else {
			g.rect(o.cx - w * 0.9, o.cy + p0 - 0.5, w * 1.8, seg).fill({ color: col, alpha: 0.1 * aMul });
			g.rect(o.cx - w * 0.5, o.cy + p0 - 0.5, w, seg).fill({ color: col, alpha: 0.32 * aMul });
			g.rect(o.cx - w * 0.16, o.cy + p0 - 0.5, w * 0.32, seg).fill({ color: 0xffffff, alpha: 0.3 * aMul });
		}
	}
	// drifting sparkle motes riding the stream (same maths in flight and at rest)
	for (let k = 0; k < 3; k++) {
		const u = (((k * 0.34 + o.flowSign * o.phase * 0.45) % 1) + 1) % 1;
		const p = -L / 2 + u * L;
		if (p < lo || p > hi) continue;
		const tw = (Math.sin(o.phase * Math.PI * 5 + k * 2.1) + 1) / 2;
		const wob = Math.sin(o.phase * Math.PI * 2.6 + k * 1.7) * W * 0.3;
		const px = o.horizontal ? p : wob;
		const py = o.horizontal ? wob : p;
		g.circle(o.cx + px, o.cy + py, 1.6 + 1.5 * tw).fill({ color: 0xffffff, alpha: (0.2 + 0.45 * tw) * aMul });
	}
};
