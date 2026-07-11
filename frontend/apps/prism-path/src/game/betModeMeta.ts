// Prism Path bet modes — drives the Buy Bonus modal cards and the RGS bet mode string.
// Keys/mode strings follow the SDK convention (uppercase client key -> lowercase math mode).
import type { BetModeMeta } from 'state-shared';

const cardBonus = new URL('../../assets/ui/cards/card_bonus.png', import.meta.url).href;
const cardSuper = new URL('../../assets/ui/cards/card_super.png', import.meta.url).href;

export const PRISM_BET_MODE_META = {
	BASE: {
		mode: 'BASE',
		costMultiplier: 1.0,
		type: 'default',
		parent: '',
		children: '',
		assets: { icon: '', dialogImage: '', dialogVolatility: '', volatility: '', button: '' },
		text: {
			title: '',
			dialog: '',
			button: '',
			betAmountLabel: '',
			tickerIdle: 'PLACE YOUR BET',
			tickerSpin: 'GOOD LUCK',
			bannerText: '',
		},
		maxWin: 5000,
	},
	BONUS: {
		mode: 'BONUS',
		costMultiplier: 100,
		type: 'buy',
		parent: '',
		children: '',
		assets: {
			icon: cardBonus,
			dialogImage: cardBonus,
			dialogVolatility: '',
			volatility: '',
			button: '',
		},
		text: {
			title: 'DRAGON BONUS',
			dialog:
				'Buy entry to the FREE SPINS feature for 100x your bet. Awards 8+ free spins with an ENHANCED chance of Prism Dragons landing. Dragons fire a path of multiplier wilds (x2 to x10) toward the board edge — crossing dragon paths MULTIPLY together. Landing dragons may become STICKY, returning to the same square every spin for the rest of the feature.',
			description: 'Free spins with an enhanced chance of Prism Dragons every spin.',
			button: 'BUY',
			betAmountLabel: 'DRAGON BONUS',
			tickerIdle: 'PLACE YOUR BET',
			tickerSpin: 'DRAGON BONUS ACTIVATED',
			bannerText: '',
		},
	},
	SUPER: {
		mode: 'SUPER',
		costMultiplier: 300,
		type: 'buy',
		parent: '',
		children: '',
		assets: {
			icon: cardSuper,
			dialogImage: cardSuper,
			dialogVolatility: '',
			volatility: '',
			button: '',
		},
		text: {
			title: 'SUPER DRAGON BONUS',
			dialog:
				'Buy entry to the SUPER FREE SPINS feature for 300x your bet. A Prism Dragon is GUARANTEED to land on every free spin, with a much higher chance of STICKY dragons that return to the same square each spin, firing a fresh multiplier path in a new direction. Crossing dragon paths multiply together for the biggest wins.',
			description: 'A dragon is GUARANTEED every spin — with far more sticky dragons.',
			button: 'BUY',
			betAmountLabel: 'SUPER DRAGON BONUS',
			tickerIdle: 'PLACE YOUR BET',
			tickerSpin: 'SUPER DRAGON BONUS ACTIVATED',
			bannerText: '',
		},
	},
} as unknown as BetModeMeta;
