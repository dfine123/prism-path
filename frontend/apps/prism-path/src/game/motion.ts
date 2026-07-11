// Prism Path — motion tokens (single source of truth for feel; see studio-motion-canon).
// Name easings by INTENT, not by curve, so retuning a curve here re-tunes the whole game.
import { quadOut, backOut, cubicOut, expoOut, sineInOut, quadIn, elasticOut } from 'svelte/easing';

export const EASE = {
	load: quadOut, // wind-up before an impact
	impact: backOut, // the land/hit — overshoot then settle
	celebrate: elasticOut, // hero lands (wobble)
	settle: expoOut, // count-ups, glides, meter rolls
	glide: cubicOut, // smooth continuous travel
	idle: sineInOut, // breathe, drift, shimmer
	collapse: quadIn, // fade / shrink away
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
