// SUPER STUDIOS — bet-UI design system ("Crystal Console").
// THE single source of truth for the interaction panel across all Super Studios games:
// geometry, type scale, glass palette, brand accent and state constants. A new game
// reskins by editing tokens here — layouts and components never hard-code visuals.
//
// Layout contract (identical in every game):
//   LEFT  zone — system: menu, buy bonus
//   CENTER zone — money truth: balance / win readouts (display-only look)
//   RIGHT zone — action gradient: [-] bet [+] -> autoplay/turbo -> HERO spin (far right)
// Rails lay out with a RUNNING CURSOR and a FLEXIBLE capsule width (capsMinW..caps.w),
// so overlap is impossible by construction at any standard-layout width.
// State language (identical on every control):
//   hover = rim-light | press = shrink to PRESS | active = gold ring | disabled = DIM alpha

export const SUPER_UI = {
	// geometry (standard-layout px; standard widths: desktop/landscape 1920, portrait 1080)
	btn: 120, // standard circular control diameter
	btnSm: 92, // secondary control diameter (menu, steppers)
	hero: 200, // hero spin diameter — breaks the rail's top edge on purpose
	railH: 176,
	railR: 34,
	railMargin: 20, // rail inset from the standard layout edges
	pad: 26, // rail inner padding
	gap: 16, // gap between controls
	gapZone: 32, // gap between zones
	caps: { w: 280, h: 112, r: 24 }, // readout capsule (portrait floating readouts)
	capsMinW: 216, // capsule floor before the whole strip scales to fit
	// buy bonus: a rounded-SQUARE star button, taller than the deck, standing just left of
	// it — aligned as part of the composed row (the Hex Bloom "paperclip" pattern)
	buy: { size: 148, r: 34 },

	// the UNIFIED CONSOLE DECK (desktop/tablet/landscape): ONE floating fully-rounded bar —
	// menu, readouts, stacked steppers, STACKED auto/turbo — with the HERO anchored on its
	// right end cap (half in, half out). Buy bonus stands DETACHED at the screen's left.
	bar: {
		h: 116,
		padX: 30,
		menu: 72, // in-bar menu button (glyph only)
		balW: 228, // readout block widths (values shrink-to-fit inside)
		winW: 178,
		betW: 142,
		stepper: 46, // stacked mini +/- diameter
		toggleStack: 64, // auto/turbo stacked OUTSIDE the deck, right of the hero
		heroPoke: 26, // how far the hero's edge reaches past the bar's end cap
	},

	// type — "Superui" = Fredoka (variable, SIL OFL), chunky geometric-round: bold + fun
	font: 'Superui',
	fs: { label: 22, value: 36, btnLabel: 19, heroLabel: 32, capsLabel: 22, barLabel: 21, barValue: 34 },

	// glass palette (deep plum glass — sits with the crystal frame's plum linework)
	color: {
		glass: 0x140d22,
		glassHi: 0x201533, // hovered / hero core
		edge: 0x54446f, // resting rim
		edgeLit: 0xbfe9ff, // hovered rim-light (ice)
		textDim: 0xa79cc4, // labels
		text: 0xffffff, // values / glyphs
		gold: 0xffd25e, // active toggles, win accent, buy bonus
		// brand prism (matches the game-side PRISM_TINTS — the Super Studios accent ramp)
		prism: [0xff5db1, 0x2bb8e8, 0x3cc85a, 0x9b3ce8, 0xffd25e],
	},

	// states
	press: 0.94, // pressed scale
	dim: 0.42, // disabled alpha
	glassAlpha: 0.9,
} as const;

const lerpChannel = (a: number, b: number, t: number, shift: number) =>
	Math.round(((a >> shift) & 255) + (((b >> shift) & 255) - ((a >> shift) & 255)) * t) << shift;

export const lerpColor = (a: number, b: number, t: number) =>
	lerpChannel(a, b, t, 16) | lerpChannel(a, b, t, 8) | lerpChannel(a, b, t, 0);

/** Sample the brand prism ramp at u (wraps, period 1) — hero ring, accent sweeps. */
export const prismAt = (u: number) => {
	const P = SUPER_UI.color.prism;
	const f = (((u % 1) + 1) % 1) * P.length;
	const i = Math.floor(f) % P.length;
	return lerpColor(P[i], P[(i + 1) % P.length], f - Math.floor(f));
};

// ---------------------------------------------------------------------------------------
// REAL LIGHT. Flat white rectangles laid over a surface read as stickers — the hard edge is
// the tell. These build actual gradients (rgba stops, so the light FADES OUT into the glass
// instead of stopping) for the two lights a glass control has:
//   sheenGradient  — the broad top-down fall of ambient light across a plate
//   specularGradient — the tight highlight where a domed key catches the source
// Both are declared in LOCAL space (0..1 of the shape's bounds), so one gradient object
// works at any control size.
// ---------------------------------------------------------------------------------------
const rgba = (hex: number, a: number) =>
	`rgba(${(hex >> 16) & 255},${(hex >> 8) & 255},${hex & 255},${a})`;

/** Top-down ambient fall for flat plates: bright lip -> quick falloff -> nothing. */
export const sheenGradient = (FillGradient: any, strength = 1) =>
	new FillGradient({
		type: 'linear',
		start: { x: 0, y: 0 },
		end: { x: 0, y: 1 },
		textureSpace: 'local',
		colorStops: [
			{ offset: 0, color: rgba(0xffffff, 0.16 * strength) },
			{ offset: 0.32, color: rgba(0xffffff, 0.045 * strength) },
			{ offset: 0.62, color: rgba(0xffffff, 0) },
			{ offset: 1, color: rgba(0x000000, 0.22 * strength) },
		],
	});

/** Inner shadow for recessed wells: dark under the top lip, fading to a lit bottom edge. */
export const innerShadowGradient = (FillGradient: any) =>
	new FillGradient({
		type: 'linear',
		start: { x: 0, y: 0 },
		end: { x: 0, y: 1 },
		textureSpace: 'local',
		colorStops: [
			{ offset: 0, color: rgba(0x000000, 0.34) },
			{ offset: 0.42, color: rgba(0x000000, 0.05) },
			{ offset: 0.85, color: rgba(0x000000, 0) },
			{ offset: 1, color: rgba(0xffffff, 0.07) },
		],
	});

/** Specular blob for domed keys — offset up-left like a single overhead source. */
export const specularGradient = (FillGradient: any, strength = 1) =>
	new FillGradient({
		type: 'radial',
		center: { x: 0.42, y: 0.3 },
		innerRadius: 0,
		outerCenter: { x: 0.42, y: 0.3 },
		outerRadius: 0.62,
		textureSpace: 'local',
		colorStops: [
			{ offset: 0, color: rgba(0xffffff, 0.3 * strength) },
			{ offset: 0.45, color: rgba(0xffffff, 0.08 * strength) },
			{ offset: 1, color: rgba(0xffffff, 0) },
		],
	});
