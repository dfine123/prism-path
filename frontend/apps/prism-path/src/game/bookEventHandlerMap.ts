import _ from 'lodash';

import { recordBookEvent, checkIsMultipleRevealEvents, type BookEventHandlerMap } from 'utils-book';
import { wasRecentUiPress } from 'components-pixi';
import { stateBet, stateUi } from 'state-shared';
import { sequence } from 'utils-shared/sequence';
import { waitForTimeout } from 'utils-shared/wait';

import { eventEmitter } from './eventEmitter';
import { playBookEvent } from './utils';
import { stateFx, boardBreathe, boardSlam } from './stateFx.svelte';
import { winLevelMap, type WinLevel, type WinLevelData } from './winLevelMap';
import { stateGame, stateGameDerived } from './stateGame.svelte';
import type { BookEvent, BookEventOfType, BookEventContext } from './typesBookEvent';
import type { Position } from './types';
import config from './config';

const winLevelSoundsPlay = ({ winLevelData }: { winLevelData: WinLevelData }) => {
	if (winLevelData?.alias === 'max') eventEmitter.broadcastAsync({ type: 'uiHide' });
	if (winLevelData?.sound?.sfx) {
		eventEmitter.broadcast({ type: 'soundOnce', name: winLevelData.sound.sfx });
	}
	if (winLevelData?.sound?.bgm) {
		eventEmitter.broadcast({ type: 'soundMusic', name: winLevelData.sound.bgm });
	}
	if (winLevelData?.type === 'big') {
		eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_bigwin_coinloop' });
	}
};

const winLevelSoundsStop = () => {
	eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_bigwin_coinloop' });
	// resume whichever bed the current game type owns (no SUPERSPIN mode in this game)
	if (stateGame.gameType === 'freegame') {
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
	} else {
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_main' });
	}
	eventEmitter.broadcastAsync({ type: 'uiShow' });
};

const animateSymbols = async ({ positions }: { positions: Position[] }) => {
	eventEmitter.broadcast({ type: 'boardShow' });
	await eventEmitter.broadcastAsync({
		type: 'boardWithAnimateSymbols',
		symbolPositions: positions,
	});
};

export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = {
	reveal: async (bookEvent: BookEventOfType<'reveal'>, { bookEvents }: BookEventContext) => {
		const isBonusGame = checkIsMultipleRevealEvents({ bookEvents });
		if (isBonusGame) {
			eventEmitter.broadcast({ type: 'stopButtonEnable' });
			recordBookEvent({ bookEvent });
		}

		stateGame.gameType = bookEvent.gameType;
		// back in the base game -> any sticky-dragon markers from a finished feature are stale
		if (bookEvent.gameType === 'basegame') {
			eventEmitter.broadcast({ type: 'stickyMarkerClear' });
		}
		// a CLICK mid-spin = "hurry up": slam the reels like the stop button / turbo would.
		// Presses that land ON a console control are exempt (wasRecentUiPress) — clicking
		// MENU or TURBO mid-spin must not double as a reel slam.
		const quickStop = () => {
			if (wasRecentUiPress()) return;
			eventEmitter.broadcast({ type: 'stopButtonClick' });
		};
		window.addEventListener('pointerdown', quickStop);
		boardBreathe(); // the board takes a breath as the reels launch
		try {
			await stateGameDerived.enhancedBoard.spin({
				revealEvent: bookEvent,
				paddingBoard: config.paddingReels[bookEvent.gameType],
			});
		} finally {
			window.removeEventListener('pointerdown', quickStop);
		}
		// NEAR-MISS (subtle, POLISH-ROADMAP 1.5): anticipation ran and the trigger whiffed
		// at exactly 2 landed scatters — a quiet descending exhale marks the decompression.
		// Skipped whenever a win presentation follows this reveal (the win owns the stage;
		// a sigh under a celebration reads as a mixed message).
		if (bookEvent.anticipation?.some(Boolean) && stateGame.scatterCounter === 2) {
			const at = bookEvents.indexOf(bookEvent);
			const rest = at === -1 ? [] : bookEvents.slice(at + 1);
			const nextReveal = rest.findIndex((e) => e.type === 'reveal');
			const untilNextSpin = nextReveal === -1 ? rest : rest.slice(0, nextReveal);
			const stageIsQuiet = !untilNextSpin.some(
				(e) => e.type === 'winInfo' || e.type === 'freeSpinTrigger',
			);
			if (stageIsQuiet) {
				eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_near_miss' });
			}
		}
		eventEmitter.broadcast({ type: 'soundScatterCounterClear' });
	},
	prismBeast: async (bookEvent: BookEventOfType<'prismBeast'>) => {
		// The beast has landed facing its direction (from the reveal). A brief charge beat of
		// anticipation before it pushes off — the travel overlay carries the full wind-up.
		// A STICKY dragon claims its square: persistent glowing border for the rest of the
		// feature (the dragon re-lands there every spin).
		if (bookEvent.sticky) {
			eventEmitter.broadcast({ type: 'stickyMarkerAdd', position: bookEvent.position });
			// CLAIM UPGRADE: on the spin a dragon BECOMES sticky, the reveal seeded its cell
			// as a plain beast (the math flags stickiness only in this event) — without this,
			// a normal dragon sat inside the igniting marker box. Upgrade the seat in the
			// same beat: crowned sticky art + badge swap in as the box lights, and the seat
			// then follows the sticky choreography (own-path exemption, dormant vacate)
			// exactly like a returning sticky. Idempotent for returning seats.
			const seat =
				stateGame.board[bookEvent.position.reel]?.reelState?.symbols?.[bookEvent.position.row];
			if (seat?.rawSymbol.name === 'WILD' && !seat.rawSymbol.sticky) {
				seat.rawSymbol = {
					...seat.rawSymbol,
					sticky: true,
					direction: bookEvent.direction ?? seat.rawSymbol.direction,
					// MULTIPLY, don't replace: an earlier beast's path crossing this seat has
					// already accumulated its factor onto the chip (revealCell's seated-beast
					// branch). The claim installs the dragon's OWN factor on top — the chip
					// must end at the coverage PRODUCT the math pays (x2 crossed by x3 = x6),
					// and the seat's own flight is accumulation-exempt so nothing double-counts.
					multiplier: (seat.rawSymbol.multiplier ?? 1) * (bookEvent.multiplier ?? 1),
				};
			}
		}
		// the ARRIVAL is a bright chime; the fuller multiplier chord belongs to the path
		// ignition later in the flight (sharing one cue made the two beats indistinct)
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_dragon_land' });
		boardSlam(0.7); // the dragon has weight — the board feels it land
		await waitForTimeout(60);
	},
	prismPath: async (bookEvent: BookEventOfType<'prismPath'>) => {
		// Hand the whole flight to the PrismBeastTravel overlay. Non-sticky: the dragon pushes
		// off, flows along the path and exits the board. STICKY: the dragon stays seated on its
		// cell (lunge + light comet fires the path). Awaiting pauses the book until it lands.
		await eventEmitter.broadcastAsync({
			type: 'prismBeastTravel',
			beast: {
				direction: bookEvent.direction as 'up' | 'down' | 'left' | 'right',
				sticky: !!bookEvent.sticky,
				multiplier: bookEvent.multiplier ?? bookEvent.cells?.[0]?.multiplier ?? 2,
				origin: bookEvent.source,
				cells: bookEvent.cells ?? [],
			},
		});
	},
	winInfo: async (bookEvent: BookEventOfType<'winInfo'>) => {
		// PRESENTATION MERGE: two paylines can share an identical winning-cell set (the
		// diagonal and the shallow-V both start rows 0,1,2 — a 3-kind pays BOTH). The math
		// pays each line (books/RTP untouched), but sweeping the same cells twice reads as
		// a double count — so same-cell wins present ONCE with the combined amount.
		const mergedByCells = new Map<string, (typeof bookEvent.wins)[number]>();
		for (const w of bookEvent.wins) {
			const key = [...w.positions].map((p) => `${p.reel},${p.row}`).sort().join('|');
			const prev = mergedByCells.get(key);
			if (prev) {
				mergedByCells.set(key, {
					...prev,
					win: (prev.win ?? 0) + (w.win ?? 0),
					meta: {
						...prev.meta,
						winWithoutMult:
							(prev.meta?.winWithoutMult ?? prev.win ?? 0) + (w.meta?.winWithoutMult ?? w.win ?? 0),
					},
				});
			} else {
				mergedByCells.set(key, w);
			}
		}
		// Lines play strictly SEQUENTIALLY, ordered by value ascending so the presentation
		// escalates and ends on the biggest hit. Per line: the prism win-line sweeps through
		// the winning cells while those symbols breathe — both awaited so nothing overlaps.
		// A CLICK during the sequence = "skip through": every paced clock runs much faster.
		const wins = [...mergedByCells.values()].sort((a, b) => (a.win ?? 0) - (b.win ?? 0));

		stateFx.winSpeed = 1;
		const speedUp = () => {
			if (wasRecentUiPress()) return; // console presses are not "skip the lines"
			stateFx.winSpeed = 5;
		};
		window.addEventListener('pointerdown', speedUp);
		try {
			await sequence(wins, async (win) => {
				eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_winlevel_small' });
				await Promise.all([
					eventEmitter.broadcastAsync({
						type: 'winLinePlay',
						positions: win.positions,
						amount: win.win,
						baseAmount: win.meta?.winWithoutMult ?? win.win,
						multiplier: win.meta?.lineMultiplier ?? 1,
					}),
					animateSymbols({ positions: win.positions }),
				]);
			});
		} finally {
			window.removeEventListener('pointerdown', speedUp);
			stateFx.winSpeed = 1;
		}
	},
	setTotalWin: async (bookEvent: BookEventOfType<'setTotalWin'>) => {
		stateBet.winBookEventAmount = bookEvent.amount;
	},
	freeSpinTrigger: async (bookEvent: BookEventOfType<'freeSpinTrigger'>) => {
		// animate scatters — skipped when the replay carries no positions (resume snapshot:
		// the celebration already happened in the original session; re-firing it against
		// the resumed mid-feature board animated cells that are not scatters)
		if (bookEvent.positions.length > 0) {
			eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_win_v2' });
			await animateSymbols({ positions: bookEvent.positions });
		}
		// show free spin intro (the day->night background swap happens UNDER the curtain)
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		await eventEmitter.broadcastAsync({
			type: 'transition',
			onCovered: () => {
				stateGame.gameType = 'freegame';
			},
		});
		eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'jng_intro_fs' });
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
		await eventEmitter.broadcastAsync({
			type: 'freeSpinIntroUpdate',
			totalFreeSpins: bookEvent.totalFs,
		});
		eventEmitter.broadcast({ type: 'freeSpinIntroHide' });
		eventEmitter.broadcast({ type: 'boardFrameGlowShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		stateUi.freeSpinCounterShow = true;
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			// explicit 0: `undefined` means "keep previous" to the counter, which showed the
			// PREVIOUS feature's final count (e.g. "8 / 12") through this trigger's tail
			current: 0,
			total: bookEvent.totalFs,
		});
		stateUi.freeSpinCounterCurrent = 0;
		stateUi.freeSpinCounterTotal = bookEvent.totalFs;
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerButtonShow' });
		eventEmitter.broadcast({ type: 'drawerFold' });
	},
	updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		stateUi.freeSpinCounterShow = true;
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			current: bookEvent.amount + 1,
			total: bookEvent.total,
		});
		stateUi.freeSpinCounterCurrent = bookEvent.amount + 1;
		stateUi.freeSpinCounterTotal = bookEvent.total;
	},
	freeSpinRetrigger: async (bookEvent: BookEventOfType<'freeSpinRetrigger'>) => {
		// RETRIGGER: an awarded outcome must be PRESENTED — without this handler the event
		// was skipped and the counter total just silently jumped on the next updateFreeSpin.
		// Scatters animate, then the counter total bumps to the new total (the following
		// updateFreeSpin repeats the same total, so this stays consistent either way).
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_win_v2' });
		await animateSymbols({ positions: bookEvent.positions });
		// "+N FREE SPINS" banner beat (awaited) — the delta vs the counter's CURRENT total
		// is what was just awarded; the bump to the new total lands as the banner leaves
		const extraSpins = bookEvent.totalFs - stateUi.freeSpinCounterTotal;
		if (extraSpins > 0) {
			await eventEmitter.broadcastAsync({ type: 'retriggerShow', extraSpins });
		}
		stateUi.freeSpinCounterTotal = bookEvent.totalFs;
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			current: stateUi.freeSpinCounterCurrent,
			total: bookEvent.totalFs,
		});
	},
	wincap: async (bookEvent: BookEventOfType<'wincap'>) => {
		// MAX WIN: the 5000x cap is the game's biggest beat — full level-10 presentation the
		// moment it's crossed. The math suppresses that spin's setWin (no double-present);
		// the feature-end outro still shows the capped total afterwards.
		const winLevelData = winLevelMap[10];
		eventEmitter.broadcast({ type: 'winShow' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({
			type: 'winUpdate',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'winHide' });
	},
	freeSpinEnd: async (bookEvent: BookEventOfType<'freeSpinEnd'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];

		// The TOTAL WIN outro plays IN the bonus dressing; the whole base-game teardown
		// (markers, gameType/night->day, frame glow, counter, music bed) happens UNDER the
		// exit curtain — mirroring the entry, where the swap hides under the curtain.
		// Tearing down in the open (the old order) visibly snapped the scene back to base
		// BEFORE the outro and read as "the game switched to base mid-bonus".
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		eventEmitter.broadcast({ type: 'freeSpinOutroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_youwon_panel' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({
			type: 'freeSpinOutroCountUp',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop(); // still freegame -> keeps the freespin bed under the outro tail
		eventEmitter.broadcast({ type: 'freeSpinOutroHide' });
		await eventEmitter.broadcastAsync({
			type: 'transition',
			onCovered: () => {
				eventEmitter.broadcast({ type: 'stickyMarkerClear' }); // feature over -> markers off
				stateGame.gameType = 'basegame';
				eventEmitter.broadcast({ type: 'boardFrameGlowHide' });
				eventEmitter.broadcast({ type: 'freeSpinCounterHide' });
				stateUi.freeSpinCounterShow = false;
				eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_main' });
			},
		});
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerUnfold' });
		eventEmitter.broadcast({ type: 'drawerButtonHide' });
	},
	setWin: async (bookEvent: BookEventOfType<'setWin'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];

		eventEmitter.broadcast({ type: 'winShow' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({
			type: 'winUpdate',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'winHide' });
	},
	finalWin: async (bookEvent: BookEventOfType<'finalWin'>) => {
		// Do nothing
	},
	// customised
	createBonusSnapshot: async (bookEvent: BookEventOfType<'createBonusSnapshot'>) => {
		const { bookEvents } = bookEvent;

		function findLastBookEvent<T>(type: T) {
			return _.findLast(bookEvents, (bookEvent) => bookEvent.type === type) as
				| BookEventOfType<T>
				| undefined;
		}

		const lastFreeSpinTriggerEvent = findLastBookEvent('freeSpinTrigger' as const);
		const lastUpdateFreeSpinEvent = findLastBookEvent('updateFreeSpin' as const);
		const lastSetTotalWinEvent = findLastBookEvent('setTotalWin' as const);

		// replay the trigger WITHOUT the scatter celebration (positions: []) and with the
		// CURRENT total (a pre-resume retrigger raised it past the original award — the
		// intro panel and counter must both show the truth at the resume point)
		if (lastFreeSpinTriggerEvent)
			await playBookEvent(
				{
					...lastFreeSpinTriggerEvent,
					positions: [],
					totalFs: lastUpdateFreeSpinEvent?.total ?? lastFreeSpinTriggerEvent.totalFs,
				},
				{ bookEvents },
			);
		if (lastUpdateFreeSpinEvent) playBookEvent(lastUpdateFreeSpinEvent, { bookEvents });
		if (lastSetTotalWinEvent) playBookEvent(lastSetTotalWinEvent, { bookEvents });
	},
};
