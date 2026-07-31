import { setup, fromPromise, assign } from 'xstate';

import { stateBet, stateBetDerived, stateModal } from 'state-shared';

import { context, type Context } from './machineContext';
import type { PrimaryMachines } from './types';

// MACHINE-LEVEL BET ADMISSION. This loop re-bets with no UI in the path (it never passes
// through idle, so every idle-gated UI guard is bypassed) — therefore IT must check what
// the UI normally would: the hold is still armed, no modal is open, and the next wager is
// affordable. Anything else ends the run cleanly.
const checkSpaceHold = fromPromise(async () => {
	if (!stateBet.isSpaceHold) throw Error('end bet');
	if (stateModal.modal !== null) throw Error('end bet');
	if (!stateBetDerived.isBetCostAvailable()) throw Error('end bet');
	// a bought feature never repeat-buys on hold — continue as BASE spins
	if (stateBetDerived.activeBetMode()?.type === 'buy') {
		stateBet.activeBetModeKey = 'BASE';
	}
});

export const createIntermediateMachineBet = ({
	newGame,
	playGame,
	endGame,
}: {
	newGame: PrimaryMachines['newGame'];
	playGame: PrimaryMachines['playGame'];
	endGame: PrimaryMachines['endGame'];
}) => {
	const machine =
		/** @xstate-layout N4IgpgJg5mDOIC5QCMwBcB0BLCAbMAxAEICiAKoqAA4D2sWaWNAdpSAB6ICMATAGwYADMMFcA7Dy4BWQQBZZgsQBoQAT24BmMRlkBOfQA4+fXWNl8pu2QF9rK1JgBm6AMYALLMygEILMNmYANxoAa38AWwBXNABDRhYidDZaenjWJA5EKQ0BWS0pHlMNGTE+FXUELlEMGRENXV4pKtFbe3QMZzR3T28wACc+mj6MKlw4xyHwjCjYtMS0ZLoGJnTQTgRs3PzCsWLFMrVEHjFBHX1TWXEzDQ0DGzsQBxGx1R8-AOCw55iK6iW0tjrKxcDAGRo8MEnRQ8crcHinc76QpSMxg3R8WwPZg0CBwNhPHD4RapFaAxCyGGHSoaEGI0oFPT1XStR7tTrdLzE5YsMkIeEGDC6O71LQGYSyMXKKlVXKIvhGc5cUwsp6jH5cgEZdYSXQYDQQrjmBrCKQHCq6U4iYQ0jQiMUaFXtMDMCAa0la7iKbSSAxiX2m4ToykVXgaQXnE5+iwNIyOhYZFLc1aZSoGWGpoRWrNWsSY6xAA */
		setup({
			types: {} as {
				context: Context;
			},
			actors: {
				newGame,
				playGame,
				endGame,
				checkSpaceHold,
			},
		}).createMachine({
			context,
			id: 'bet',
			initial: 'fetching',
			states: {
				fetching: {
					invoke: {
						id: 'newGame',
						src: 'newGame',
						onDone: [
							{
								actions: assign(({ context: _, event }) => event.output),
								target: 'play',
							},
						],
						// output: ,
						onError: [
							{
								target: 'end',
							},
						],
					},
				},
				play: {
					invoke: {
						id: 'playGame',
						src: 'playGame',
						input: ({ context }) => ({
							bet: context.bet,
						}),
						onDone: [
							{
								target: 'ending',
							},
						],
						// a handler throw must END the round, not kill the actor — an
						// unhandled invoke error stopped the whole game machine and froze
						// the session with every visual latched
						onError: [
							{
								target: 'end',
							},
						],
					},
				},
				ending: {
					invoke: {
						id: 'endGame',
						src: 'endGame',
						input: ({ context }) => ({
							bet: context.bet,
							rawBet: context.rawBet,
						}),
						onDone: [
							{
								target: 'checkSpaceHold',
							},
						],
					},
				},
				checkSpaceHold: {
					invoke: {
						id: 'checkSpaceHold',
						src: 'checkSpaceHold',
						onDone: 'fetching',
						onError: 'end',
					},
				},
				end: {
					type: 'final',
				},
			},
		});

	return machine;
};
