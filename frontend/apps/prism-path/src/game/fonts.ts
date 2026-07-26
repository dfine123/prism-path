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
