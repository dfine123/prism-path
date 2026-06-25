// Forced Prism Path scenario books produced by math/games/prism_path/scenario.py.
// Each is a single book {id, payoutMultiplier, events, ...}; stories replay events via playBet.
import single from './scenarios/single.json';
import overlap from './scenarios/overlap.json';
import whiff from './scenarios/whiff.json';
import nearMax from './scenarios/near-max.json';
import zero from './scenarios/zero.json';
import rightPair from './scenarios/right-pair.json';

export const scenarios = { single, overlap, whiff, nearMax, zero, rightPair } as const;
