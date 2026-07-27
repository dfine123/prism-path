import { type SpinningReelSymbolState } from 'utils-slots';
import type config from './config';

export type SymbolName = keyof typeof config.symbols;
export type Direction = 'up' | 'down' | 'left' | 'right';
export type RawSymbol = {
	name: SymbolName;
	multiplier?: number;
	scatter?: boolean;
	wild?: boolean;
	direction?: Direction; // Prism Beast: which way it faces / fires
	sticky?: boolean; // STICKY dragon: its square is claimed for the whole feature
	// STICKY seat whose dragon has FLOWN this spin: the seat renders as a TRAIL CELL like
	// the rest of its path (no dragon art; the glowing marker box outlines the claim) until
	// the next reveal re-seeds the seat (fresh rawSymbol, no dormant) and the dragon drops
	// back in.
	dormant?: boolean;
	// frontend-only: this WILD was converted to a prism-trail cell by a flight (books never
	// set it). Distinguishes a trail cell from an UNFIRED beast's seat that another flight
	// crossed — the seat keeps its dragon (and accumulates the product) until it fires.
	trail?: boolean;
};
export type BetMode = keyof typeof config.betModes;
export type GameType = keyof typeof config.paddingReels;

export const SYMBOL_STATES = [
	'static',
	'spin',
	'land',
	'win',
	'postWinStatic',
	'explosion',
] as const;

export type SymbolState = SpinningReelSymbolState | (typeof SYMBOL_STATES)[number];

export type Position = {
	reel: number;
	row: number;
};
