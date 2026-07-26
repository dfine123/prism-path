// Prism Path display font — single source of truth for in-game text styling.
// Family "Prism" = Chango (SIL OFL, static/assets/fonts/prism/) — chunky, modern, and
// distinctive (replaced Lilita One, which read as placeholder-generic).
// FINISHED treatment (replaced the flat black-fill/white-stroke sticker look): warm
// cream fill + deep plum stroke + a soft dark drop shadow, so win numbers and badges
// read as crafted game type on the dark board. Stroke/shadow scale with size so small
// counters and huge win numbers keep the same weight relationship.
import type * as PIXI from 'pixi.js';

export const PRISM_FONT_FAMILY = 'Prism';

export const prismStyle = (
	fontSize: number,
	overrides: Partial<PIXI.TextStyleOptions> = {},
): Partial<PIXI.TextStyleOptions> => ({
	fontFamily: PRISM_FONT_FAMILY,
	fontSize,
	fill: 0xfff4dc,
	stroke: { color: 0x241131, width: Math.max(3, Math.round(fontSize * 0.11)), join: 'round' },
	dropShadow: {
		color: 0x160a24,
		alpha: 0.55,
		distance: Math.max(2, Math.round(fontSize * 0.07)),
		angle: Math.PI / 2.6,
		blur: Math.max(1, Math.round(fontSize * 0.05)),
	},
	...overrides,
});

// Numeral variant for the multiplier chips. Family "Prismnum" = Righteous (SIL OFL,
// static/assets/fonts/prismnum/) — slimmer and geometric, because Chango's heavy counters
// blob together at chip size. Same cream/plum palette as prismStyle so the two read as one
// type family; stroke and shadow are proportionally lighter to match the lighter letterforms.
export const PRISM_NUM_FONT_FAMILY = 'Prismnum';

export const prismNumStyle = (
	fontSize: number,
	overrides: Partial<PIXI.TextStyleOptions> = {},
): Partial<PIXI.TextStyleOptions> => ({
	fontFamily: PRISM_NUM_FONT_FAMILY,
	fontSize,
	fill: 0xfff4dc,
	stroke: { color: 0x241131, width: Math.max(2, Math.round(fontSize * 0.08)), join: 'round' },
	dropShadow: {
		color: 0x160a24,
		alpha: 0.5,
		distance: Math.max(2, Math.round(fontSize * 0.06)),
		angle: Math.PI / 2.6,
		blur: Math.max(1, Math.round(fontSize * 0.04)),
	},
	...overrides,
});

// Largest font size (<= baseSize) at which `text` fits inside maxWidth — measured with the
// real font metrics, so "128X" shrinks to stay inside its chip instead of flooding over it.
// The stroke straddles the glyph outline, so half of it counts toward occupied width.
let measureCtx: CanvasRenderingContext2D | null = null;
export const fitFontSize = (
	text: string,
	baseSize: number,
	maxWidth: number,
	family: string = PRISM_NUM_FONT_FAMILY,
): number => {
	let width = 0;
	if (typeof document !== 'undefined') {
		measureCtx ??= document.createElement('canvas').getContext('2d');
		if (measureCtx) {
			measureCtx.font = `${baseSize}px ${family}, sans-serif`;
			width = measureCtx.measureText(text).width;
		}
	}
	if (!width) width = text.length * baseSize * 0.62; // measurement unavailable — estimate
	width += baseSize * 0.08; // half the proportional stroke on each side
	return width <= maxWidth ? baseSize : Math.max(12, Math.floor((baseSize * maxWidth) / width));
};
