// Prism Path frontend config. Mirrors math/games/prism_path (5x5, 40 lines, base mode).
// Only `symbols` (-> SymbolName), `betModes` (-> BetMode), `paddingReels` (-> GameType +
// cosmetic reel-spin fill) are consumed at type/runtime; the rest is metadata/parity.

const mk = (names: string) => names.trim().split(/\s+/).map((name) => ({ name }));

// Cosmetic scroll-fill for the pre-reveal reel spin (never affects outcomes). No WILD/SCAT.
const FILL = mk('L1 H1 L3 L5 H2 L2 L4 H3 L1 H4 L5 L2 H1 L3 L4 H2 L5 L1 H3 L4 L2 H4 L3 L5 H1');
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
			rtp: 0.96,
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
		'10': [1, 2, 3, 2, 1],
		'11': [3, 2, 1, 2, 3],
		'12': [0, 0, 1, 0, 0],
		'13': [4, 4, 3, 4, 4],
		'14': [1, 1, 2, 1, 1],
		'15': [3, 3, 2, 3, 3],
		'16': [2, 2, 1, 2, 2],
		'17': [2, 2, 3, 2, 2],
		'18': [0, 1, 0, 1, 0],
		'19': [4, 3, 4, 3, 4],
		'20': [1, 0, 1, 0, 1],
		'21': [3, 4, 3, 4, 3],
		'22': [0, 2, 4, 2, 0],
		'23': [4, 2, 0, 2, 4],
		'24': [1, 2, 1, 2, 1],
		'25': [3, 2, 3, 2, 3],
		'26': [0, 0, 2, 0, 0],
		'27': [4, 4, 2, 4, 4],
		'28': [2, 1, 0, 1, 2],
		'29': [2, 3, 4, 3, 2],
		'30': [0, 1, 1, 1, 0],
		'31': [4, 3, 3, 3, 4],
		'32': [1, 1, 0, 1, 1],
		'33': [3, 3, 4, 3, 3],
		'34': [0, 2, 0, 2, 0],
		'35': [4, 2, 4, 2, 4],
		'36': [1, 3, 1, 3, 1],
		'37': [3, 1, 3, 1, 3],
		'38': [2, 0, 2, 0, 2],
		'39': [2, 4, 2, 4, 2],
		'40': [0, 4, 0, 4, 0],
	},
	symbols: {
		L1: { paytable: [{ '5': 1.0 }, { '4': 0.5 }, { '3': 0.25 }] },
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
