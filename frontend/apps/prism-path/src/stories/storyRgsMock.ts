// STORYBOOK-ONLY in-page RGS: patches window.fetch so the REAL bet pipeline works
// offline — the actual SPIN button (and autoplay/turbo/buys) drives the actual xstate
// machine, which "requests" a bet and receives a random REAL book for the active mode.
// A tiny mock wallet answers the balance calls, so balance/win math behaves like live.
// This file must never be imported by app code — stories only.
import { stateBet } from 'state-shared';
import { API_AMOUNT_MULTIPLIER } from 'constants-shared/bet';

import baseBooks from './data/base_books';
import bonusBooks from './data/bonus_books';
import superBooks from './data/super_books';
import huntBooks from './data/hunt_books';
import dragon3Books from './data/dragon3_books';
import dragon5Books from './data/dragon5_books';

type StoryBook = { payoutMultiplier?: number; events: unknown[] };

const POOLS: Record<string, StoryBook[]> = {
	BASE: baseBooks as StoryBook[],
	BONUS: bonusBooks as StoryBook[],
	SUPER: superBooks as StoryBook[],
	HUNT: huntBooks as StoryBook[],
	DRAGON3: dragon3Books as StoryBook[],
	DRAGON5: dragon5Books as StoryBook[],
};
// what the RGS charges per mode (multiple of the base bet amount) — mirrors game_config costs
const COST: Record<string, number> = {
	BASE: 1,
	BONUS: 100,
	SUPER: 300,
	HUNT: 2.5,
	DRAGON3: 4,
	DRAGON5: 22.5,
};

const START_BALANCE = 10_000; // dollars

const wallet = {
	amount: START_BALANCE * API_AMOUNT_MULTIPLIER, // API micro-units
	pendingWin: 0, // credited by /wallet/end-round, like the live RGS
};

let installed = false;

export const installStoryRgsMock = () => {
	if (installed || typeof window === 'undefined') return;
	installed = true;

	stateBet.balanceAmount = START_BALANCE; // authenticate never runs in storybook — seed it

	const realFetch = window.fetch.bind(window);
	const respond = (data: unknown) =>
		new Response(JSON.stringify(data), { status: 200, headers: { 'Content-Type': 'application/json' } });
	const balancePayload = () => ({ amount: wallet.amount, currency: stateBet.currency || 'USD' });

	window.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
		const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;

		if (url.includes('/wallet/play')) {
			const body = init?.body ? JSON.parse(String(init.body)) : {};
			const mode: string = body.mode ?? 'BASE';
			const pool = POOLS[mode] ?? POOLS.BASE;
			const book = pool[Math.floor(Math.random() * pool.length)];
			const baseWager: number = body.amount ?? API_AMOUNT_MULTIPLIER;
			wallet.amount = Math.max(0, wallet.amount - baseWager * (COST[mode] ?? 1));
			// payoutMultiplier is relative to the BASE bet amount (buy cost carries the mode
			// RTP) and the books store it in x100 INT units (1100 = 11.00x) — scale it down
			wallet.pendingWin = Math.round((baseWager * (book.payoutMultiplier ?? 0)) / 100);
			return respond({
				balance: balancePayload(),
				round: { ...book, state: book.events, mode, event: 0, active: true },
			});
		}
		if (url.includes('/wallet/end-round')) {
			wallet.amount += wallet.pendingWin;
			wallet.pendingWin = 0;
			return respond({ balance: balancePayload() });
		}
		if (url.includes('/wallet/authenticate')) {
			return respond({ balance: balancePayload() });
		}
		if (url.includes('/bet/event')) {
			return respond({});
		}
		return realFetch(input as RequestInfo, init);
	}) as typeof fetch;
};
