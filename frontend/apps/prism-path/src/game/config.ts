// Prism Path frontend config. Mirrors math/games/prism_path (5x5, 17 lines, base mode).
// Only `symbols` (-> SymbolName), `betModes` (-> BetMode), `paddingReels` (-> GameType +
// cosmetic reel-spin fill) are consumed at type/runtime; the rest is metadata/parity.

const mk = (names: string) => names.trim().split(/\s+/).map((name) => ({ name }));

// Cosmetic scroll-fill for the pre-reveal reel spin (never affects outcomes). No WILD/SCAT.
const FILL = mk('H1 L3 L5 H2 L2 L4 H3 L5 H4 L5 L2 H1 L3 L4 H2 L5 L4 H3 L4 L2 H4 L3 L5 H1 L2');
const PADDING_REELS = [FILL, FILL, FILL, FILL, FILL];

export default {
	providerName: 'sample_provider',
	gameName: 'prism_path',
	gameID: 'prism_path',
	rtp: 0.96,
	numReels: 5,
	numRows: [5, 5, 5, 5, 5],
	betModes: {
		base: {
			cost: 1.0,
			feature: true,
			buyBonus: false,
			rtp: 0.965,
			max_win: 5000.0,
		},
		bonus: {
			cost: 100.0,
			feature: false,
			buyBonus: true,
			rtp: 0.965,
			max_win: 5000.0,
		},
		super: {
			cost: 300.0,
			feature: false,
			buyBonus: true,
			rtp: 0.965,
			max_win: 5000.0,
		},
	},
	paylines: {
		'1': [0, 0, 0, 0, 0],
		'2': [1, 1, 1, 1, 1],
		'3': [2, 2, 2, 2, 2],
		'4': [3, 3, 3, 3, 3],
		'5': [4, 4, 4, 4, 4],
		'6': [0, 1, 2, 3, 4],
		'7': [4, 3, 2, 1, 0],
		'8': [0, 1, 2, 1, 0],
		'9': [4, 3, 2, 3, 4],
		'10': [2, 1, 0, 1, 2],
		'11': [2, 3, 4, 3, 2],
		'12': [0, 1, 0, 1, 0],
		'13': [4, 3, 4, 3, 4],
		'14': [1, 0, 1, 0, 1],
		'15': [3, 4, 3, 4, 3],
		'16': [2, 1, 2, 1, 2],
		'17': [2, 3, 2, 3, 2],
	},
	symbols: {
		L2: { paytable: [{ '5': 1.0 }, { '4': 0.5 }, { '3': 0.25 }] },
		L3: { paytable: [{ '5': 1.0 }, { '4': 0.5 }, { '3': 0.25 }] },
		L4: { paytable: [{ '5': 1.0 }, { '4': 0.5 }, { '3': 0.25 }] },
		L5: { paytable: [{ '5': 1.0 }, { '4': 0.5 }, { '3': 0.25 }] },
		H1: { paytable: [{ '5': 5.0 }, { '4': 1.5 }, { '3': 0.5 }] },
		H2: { paytable: [{ '5': 5.0 }, { '4': 1.5 }, { '3': 0.5 }] },
		H3: { paytable: [{ '5': 5.0 }, { '4': 1.5 }, { '3': 0.5 }] },
		H4: { paytable: [{ '5': 5.0 }, { '4': 1.5 }, { '3': 0.5 }] },
		WILD: { special_properties: ['wild', 'multiplier'] },
		SCAT: { special_properties: ['scatter'] },
	},
	paddingReels: {
		basegame: PADDING_REELS,
		freegame: PADDING_REELS,
	},
};
