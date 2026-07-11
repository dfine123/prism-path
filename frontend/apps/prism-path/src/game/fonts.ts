// Prism Path display font — single source of truth for in-game text styling.
// Family "Prism" = Lilita One (SIL OFL, static/assets/fonts/prism/). Bold, lightly cartoonish.
// Current art direction: BLACK base + WHITE stroke (user-locked); stroke scales with size so
// small counters and huge win numbers keep the same weight relationship.
import type * as PIXI from 'pixi.js';

export const PRISM_FONT_FAMILY = 'Prism';

export const prismStyle = (
	fontSize: number,
	overrides: Partial<PIXI.TextStyleOptions> = {},
): Partial<PIXI.TextStyleOptions> => ({
	fontFamily: PRISM_FONT_FAMILY,
	fontSize,
	fill: 0x000000,
	stroke: { color: 0xffffff, width: Math.max(3, Math.round(fontSize * 0.12)), join: 'round' },
	...overrides,
});
