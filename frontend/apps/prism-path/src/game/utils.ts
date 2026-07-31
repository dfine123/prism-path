import _ from 'lodash';
import { stateBet } from 'state-shared';
import { createPlayBookUtils } from 'utils-book';
import { createGetEmptyPaddedBoard } from 'utils-slots';

import { SYMBOL_SIZE, CELL_W, REEL_PADDING, SYMBOL_INFO_MAP, BOARD_DIMENSIONS } from './constants';
import { eventEmitter } from './eventEmitter';
import { stateFx } from './stateFx.svelte';
import type { Bet, BookEventOfType } from './typesBookEvent';
import { bookEventHandlerMap } from './bookEventHandlerMap';
import type { RawSymbol, SymbolState } from './types';

// general utils
export const { getEmptyBoard } = createGetEmptyPaddedBoard({ reelsDimensions: BOARD_DIMENSIONS });
export const { playBookEvent, playBookEvents } = createPlayBookUtils({ bookEventHandlerMap });

// RE-ENTRANCY LATCH: exactly one book plays at a time. Every playback path — the bet
// machine, autoplay, resume, and the storybook Action buttons — funnels through playBet,
// so this latch is the one place that makes CONCURRENT playback impossible (a second
// round fighting the first for the same reels/gameType was the "bonus torn down to base
// mid-flow" incident). The EnableGameActor seam also refuses BET while this is true, so
// the machine can't even wager during a foreign playback.
let bookPlaying = false;
export const isBookPlaying = () => bookPlaying;

// PRESENTATION RESET at round start: normally every broadcast here is a no-op (the
// previous round released everything on its own way out), but if a playback ever died
// mid-flight (handler throw), the latched bonus dressing must not leak into the next
// round. Cheap, idempotent, and only touches hide/reset surfaces.
const resetPresentation = () => {
	eventEmitter.broadcast({ type: 'winHide' });
	eventEmitter.broadcast({ type: 'freeSpinIntroHide' });
	eventEmitter.broadcast({ type: 'freeSpinOutroHide' });
	stateFx.winSpeed = 1;
};

export const playBet = async (bet: Bet) => {
	if (bookPlaying) return;
	bookPlaying = true;
	try {
		resetPresentation();
		stateBet.winBookEventAmount = 0;
		await playBookEvents(bet.state);
	} finally {
		bookPlaying = false;
		// re-arm the stop latch even when a handler threw — otherwise STOP (and the
		// forced-turbo reset that rides it) stays dead for the rest of the session
		eventEmitter.broadcast({ type: 'stopButtonEnable' });
	}
};

// resume bet
const BOOK_EVENT_TYPES_TO_RESERVE_FOR_SNAPSHOT = [
	'freeSpinTrigger',
	'updateFreeSpin',
	'setTotalWin',
];

export const convertTorResumableBet = (betToResume: Bet) => {
	const resumingIndex = Number(betToResume.event);
	const bookEventsBeforeResume = betToResume.state.filter(
		(_, eventIndex) => eventIndex < resumingIndex,
	);
	const bookEventsAfterResume = betToResume.state.filter(
		(_, eventIndex) => eventIndex >= resumingIndex,
	);

	const bookEventToCreateSnapshot: BookEventOfType<'createBonusSnapshot'> = {
		index: 0,
		type: 'createBonusSnapshot',
		bookEvents: bookEventsBeforeResume.filter((bookEvent) =>
			BOOK_EVENT_TYPES_TO_RESERVE_FOR_SNAPSHOT.includes(bookEvent.type),
		),
	};

	const stateToResume = [bookEventToCreateSnapshot, ...bookEventsAfterResume];

	return { ...betToResume, state: stateToResume };
};

// other utils
export const getSymbolX = (reelIndex: number) => CELL_W * (reelIndex + REEL_PADDING);
export const getSymbolY = (symbolIndexOfBoard: number) => (symbolIndexOfBoard + 0.5) * SYMBOL_SIZE;

const BEAST_ASSET = { up: 'beastUp', down: 'beastDown', left: 'beastLeft', right: 'beastRight' } as const;
// sticky dragon faces its fresh direction each re-land (rotations of the down-facing art)
const STICKY_ASSET = { up: 'stickyUp', down: 'stickyDown', left: 'stickyLeft', right: 'stickyRight' } as const;

export const getSymbolInfo = ({
	rawSymbol,
	state,
}: {
	rawSymbol: RawSymbol;
	state: SymbolState;
}) => {
	const info = SYMBOL_INFO_MAP[rawSymbol.name][state];
	// A STICKY dragon renders its dedicated crowned-guardian symbol (its claimed square also
	// carries the glowing border marker); a normal WILD renders the directional bust.
	if (rawSymbol.name === 'WILD' && rawSymbol.sticky) {
		return {
			...info,
			assetKey: rawSymbol.direction ? STICKY_ASSET[rawSymbol.direction] : 'WILDSTICKY',
		};
	}
	if (rawSymbol.name === 'WILD' && rawSymbol.direction) {
		return { ...info, assetKey: BEAST_ASSET[rawSymbol.direction] };
	}
	return info;
};
