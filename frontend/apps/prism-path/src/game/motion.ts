// Prism Path — motion tokens (single source of truth for feel; see studio-motion-canon).
// Name easings by INTENT, not by curve, so retuning a curve here re-tunes the whole game.
import { quadOut, backOut, cubicOut, expoOut, sineInOut, quadIn, elasticOut } from 'svelte/easing';

// backOut with a reduced overshoot (~7% vs backOut's ~10%) — for physical settles where the
// full curve reads as rubbery (reel bounce-back, land cushions).
const backOutSoft = (t: number) => {
	const s = 1.2;
	const u = t - 1;
	return u * u * ((s + 1) * u + s) + 1;
};

export const EASE = {
	load: quadOut, // wind-up before an impact
	impact: backOut, // the land/hit — overshoot then settle
	cushion: backOutSoft, // physical settle — rise a hair past rest, then relax
	celebrate: elasticOut, // hero lands (wobble)
	settle: expoOut, // count-ups, glides, meter rolls
	glide: cubicOut, // smooth continuous travel
	idle: sineInOut, // breathe, drift, shimmer
	collapse: quadIn, // fade / shrink away
	launch: quadIn, // accelerating dive from standstill (reel spin-up — no wind-up lift)
} as const;

// ms @ 1x (divide by timeScale at the call site if one is introduced).
export const DUR = {
	flick: 70,
	snap: 110,
	pop: 150,
	beat: 220,
	settle: 300,
	hold: 160,
	glide: 240,
} as const;

// clamp + eased-lerp helpers for hand-driven (rAF) animations.
export const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// ---- prism light palette (single source: beast trail, wild cells, win fx) ----
export const PRISM_TINTS = [0xff5db1, 0x2bb8e8, 0x3cc85a, 0x9b3ce8, 0xffd25e];

export const lerpColor = (a: number, b: number, t: number) => {
	const ar = (a >> 16) & 255,
		ag = (a >> 8) & 255,
		ab = a & 255;
	const br = (b >> 16) & 255,
		bg = (b >> 8) & 255,
		bb = b & 255;
	return (
		(Math.round(ar + (br - ar) * t) << 16) |
		(Math.round(ag + (bg - ag) * t) << 8) |
		Math.round(ab + (bb - ab) * t)
	);
};

// sample the prism palette at any real u (wraps smoothly, period 1)
export const paletteAt = (u: number) => {
	const P = PRISM_TINTS.length;
	const f = (((u % 1) + 1) % 1) * P;
	const i = Math.floor(f) % P;
	return lerpColor(PRISM_TINTS[i], PRISM_TINTS[(i + 1) % P], f - Math.floor(f));
};
