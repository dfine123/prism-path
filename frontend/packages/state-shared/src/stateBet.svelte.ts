import type { BaseBet } from 'utils-bet';
import { stateMeta } from './stateMeta.svelte';
import { stateConfig } from './stateConfig.svelte';

export type Currency = string;
export type BetToResume = BaseBet | null;
export type BetModeKey = string;

export const stateBet = $state({
	currency: 'USD' as Currency,
	balanceAmount: 0,
	betAmount: 1,
	wageredBetAmount: 1,
	betToResume: null as BetToResume,
	activeBetModeKey: 'BASE' as BetModeKey,
	winBookEventAmount: 0,
	autoSpinsLoss: 0,
	autoSpinsCounter: 0,
	autoSpinsLossLimitAmount: Infinity,
	autoSpinsSingleWinLimitAmount: Infinity,
	isSpaceHold: false,
	isTurbo: false,
	// the PLAYER'S turbo choice (persistent presses only) — runtime forcing (stop-slam,
	// space-hold) flips isTurbo but must not repaint the player's toggle
	isTurboUser: false,
});

const correctBetAmount = (value: number) => {
	if (value <= 0) return 0;
	const costMultiplier = betCostMultiplier();
	if (costMultiplier === 0) return 0;
	const max = stateBet.balanceAmount / costMultiplier;
	if (value < max) return value;
	// AFFORDABILITY CLAMP SNAPS DOWN TO A VALID BET LEVEL. The raw quotient
	// (balance / costMultiplier) is generally NOT a selectable bet — with a fractional
	// cost multiplier it is not even a clean micro-unit amount (balance 9.999999 / 2.5 =
	// 3.9999996 -> 3999999.6 micro-units on the wire). The RGS requires step-aligned
	// integer amounts, so an unsnapped clamp produced wagers it must reject.
	const options = [...stateConfig.betAmountOptions].sort((a, b) => a - b);
	const affordable = options.filter((option) => option <= max);
	if (affordable.length > 0) return affordable[affordable.length - 1];
	// nothing is affordable: fall back to the smallest level (the bet-cost gate then
	// disables spinning rather than sending an off-ladder amount)
	return options[0] ?? 0;
};

const setBetAmount = (value: number) => {
	stateBet.betAmount = correctBetAmount(value);
};

const updateBetAmount = (update: (value: number) => number) => {
	stateBet.betAmount = correctBetAmount(update(stateBet.betAmount));
};

let isTurboLocked = false;

const updateIsTurbo = (value: boolean, options: { persistent: boolean }) => {
	const { persistent } = options;

	if (!persistent && isTurboLocked) return;
	if (persistent) {
		isTurboLocked = value;
		stateBet.isTurboUser = value;
	}

	stateBet.isTurbo = value;
};

const activeBetMode = () => stateMeta.betModeMeta?.[stateBet.activeBetModeKey.toUpperCase()]
	?? stateMeta.betModeMeta?.[stateBet.activeBetModeKey.toLowerCase()]
	?? null;
const isContinuousBet = () => stateBet.autoSpinsCounter > 1 || stateBet.isSpaceHold;
const timeScale = () => (stateBet.isTurbo ? 2 : 1);
// activeBetMode() returns null for any key missing from betModeMeta — an unguarded
// deref threw a TypeError inside every consumer (bet buttons, cost checks, the machine)
const betCostMultiplier = () => {
	const mode = stateBetDerived.activeBetMode();
	return mode?.type === 'activate' ? (mode.costMultiplier ?? 1) : 1;
};
const betCost = () => stateBet.betAmount * betCostMultiplier();
const isBetCostAvailable = () => betCost() > 0 && betCost() <= stateBet.balanceAmount;
const hasAutoBetCounter = () => stateBet.autoSpinsCounter !== 0;

export const stateBetDerived = {
	setBetAmount,
	updateBetAmount,
	updateIsTurbo,
	activeBetMode,
	isContinuousBet,
	timeScale,
	betCost,
	isBetCostAvailable,
	hasAutoBetCounter,
};
