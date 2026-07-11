export default {
	// ---- Prism Path — every visual asset is generated/owned by this game (no template art).
	// Motion/FX are code-driven (WinBox, PrismBeastTravel, WinLines, PrismPanel, transitions).

	// Prism display font (Lilita One, SIL OFL — license in fonts/prism/OFL.txt). Loaded as a
	// web font; PixiJS registers the family as "Prism" (from the filename) and BitmapText
	// generates its atlas dynamically from the style (black fill + white stroke).
	prismFont: {
		type: 'font',
		src: new URL('../../assets/fonts/prism/prism.ttf', import.meta.url).href,
		preload: true,
	},

	// backgrounds (cover-cropped at render; 1376x768 source)
	bgBase: { type: 'sprite', src: new URL('../../assets/backgrounds/bg_base.png', import.meta.url).href, preload: true },
	bgFeature: { type: 'sprite', src: new URL('../../assets/backgrounds/bg_feature.png', import.meta.url).href, preload: true },

	// UI art
	prismFrameEdge: { type: 'sprite', src: new URL('../../assets/ui/prismFrameEdge.png', import.meta.url).href },
	// board-frame CANDIDATES (dev toggle via DevFramePanel; unused ones removed once locked)
	board1: { type: 'sprite', src: new URL('../../assets/ui/frames/board1.png', import.meta.url).href },
	board2: { type: 'sprite', src: new URL('../../assets/ui/frames/board2.png', import.meta.url).href },
	board3: { type: 'sprite', src: new URL('../../assets/ui/frames/board3.png', import.meta.url).href },
	board4: { type: 'sprite', src: new URL('../../assets/ui/frames/board4.png', import.meta.url).href },
	logo: { type: 'sprite', src: new URL('../../assets/ui/logo.png', import.meta.url).href, preload: true },

	// --- symbols (keys match the math reveal board names: L2-L5/H1-H4/WILD/SCAT) ---
	L2: { type: 'sprite', src: new URL('../../assets/symbols/L2.png', import.meta.url).href },
	L3: { type: 'sprite', src: new URL('../../assets/symbols/L3.png', import.meta.url).href },
	L4: { type: 'sprite', src: new URL('../../assets/symbols/L4.png', import.meta.url).href },
	L5: { type: 'sprite', src: new URL('../../assets/symbols/L5.png', import.meta.url).href },
	H1: { type: 'sprite', src: new URL('../../assets/symbols/H1.png', import.meta.url).href },
	H2: { type: 'sprite', src: new URL('../../assets/symbols/H2.png', import.meta.url).href },
	H3: { type: 'sprite', src: new URL('../../assets/symbols/H3.png', import.meta.url).href },
	H4: { type: 'sprite', src: new URL('../../assets/symbols/H4.png', import.meta.url).href },
	WILD: { type: 'sprite', src: new URL('../../assets/symbols/WILD.png', import.meta.url).href },
	WILDSTICKY: { type: 'sprite', src: new URL('../../assets/symbols/WILDSTICKY.png', import.meta.url).href },
	SCAT: { type: 'sprite', src: new URL('../../assets/symbols/SCAT.png', import.meta.url).href },
	// Prism Beast travel overlay — directional busts (picked by facing direction).
	prismBeast: { type: 'sprite', src: new URL('../../assets/symbols/prismBeast.png', import.meta.url).href },
	beastUp: { type: 'sprite', src: new URL('../../assets/symbols/beastUp.png', import.meta.url).href },
	beastDown: { type: 'sprite', src: new URL('../../assets/symbols/beastDown.png', import.meta.url).href },
	beastLeft: { type: 'sprite', src: new URL('../../assets/symbols/beastLeft.png', import.meta.url).href },
	beastRight: { type: 'sprite', src: new URL('../../assets/symbols/beastRight.png', import.meta.url).href },

	// audio (placeholder template cues — sound design is a later, separate pass)
	sound: {
		type: 'audio',
		src: new URL('../../assets/audio/sounds.json', import.meta.url).href,
		preload: true,
	},
} as const;
