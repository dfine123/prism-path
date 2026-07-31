// Prism Path bet modes — drives the Buy Bonus modal cards and the RGS bet mode string.
// Keys/mode strings follow the SDK convention (uppercase client key -> lowercase math mode).
import type { BetModeMeta } from 'state-shared';

const cardBonus = new URL('../../assets/ui/cards/card_bonus.png', import.meta.url).href;
const cardSuper = new URL('../../assets/ui/cards/card_super.png', import.meta.url).href;
// feature-spin cards use the game's own art until dedicated card art is generated
const cardHunt = new URL('../../assets/symbols/SCAT.png', import.meta.url).href;
const cardDragon = new URL('../../assets/symbols/WILDSTICKY.png', import.meta.url).href;

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
	HUNT: {
		mode: 'HUNT',
		costMultiplier: 2.5,
		type: 'activate',
		parent: '',
		children: '',
		assets: {
			icon: cardHunt,
			dialogImage: cardHunt,
			dialogVolatility: '',
			volatility: '',
			button: '',
		},
		text: {
			title: 'BONUS HUNT',
			dialog:
				'Every spin costs 2.5x your bet and carries 4x THE CHANCE of triggering the FREE SPINS feature. All other rules are unchanged — dragons, paths and paylines play exactly as normal. Deactivate at any time.',
			description: '4x the chance of FREE SPINS on every spin.',
			button: 'ACTIVATE',
			betAmountLabel: 'BONUS HUNT',
			tickerIdle: 'BONUS HUNT ACTIVE',
			tickerSpin: 'HUNTING THE BONUS',
			bannerText: '',
		},
	},
	DRAGON3: {
		mode: 'DRAGON3',
		costMultiplier: 4,
		type: 'buy',
		parent: '',
		children: '',
		assets: {
			icon: cardDragon,
			dialogImage: cardDragon,
			dialogVolatility: '',
			volatility: '',
			button: '',
		},
		text: {
			title: 'TRIPLE DRAGONS',
			dialog:
				'One spin with THREE Prism Dragons GUARANTEED for 4x your bet. Every dragon fires a path of multiplier wilds — crossing paths MULTIPLY together. Scatters still land naturally, so the spin can also trigger FREE SPINS.',
			description: 'One spin, THREE dragons guaranteed.',
			button: 'BUY',
			betAmountLabel: 'TRIPLE DRAGONS',
			tickerIdle: 'PLACE YOUR BET',
			tickerSpin: 'TRIPLE DRAGONS ACTIVATED',
			bannerText: '',
		},
	},
	DRAGON5: {
		mode: 'DRAGON5',
		costMultiplier: 22.5,
		type: 'buy',
		parent: '',
		children: '',
		assets: {
			icon: cardDragon,
			dialogImage: cardDragon,
			dialogVolatility: '',
			volatility: '',
			button: '',
		},
		text: {
			title: 'DRAGON STORM',
			dialog:
				'One spin with FIVE Prism Dragons GUARANTEED for 22.5x your bet. Paths of multiplier wilds tear across the board and every crossing MULTIPLIES — the most explosive single spin in the game. A dragon already facing the edge fires off the board. Scatters still land naturally, so the spin can also trigger FREE SPINS.',
			description: 'One spin, FIVE dragons guaranteed — paths everywhere.',
			button: 'BUY',
			betAmountLabel: 'DRAGON STORM',
			tickerIdle: 'PLACE YOUR BET',
			tickerSpin: 'DRAGON STORM ACTIVATED',
			bannerText: '',
		},
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
