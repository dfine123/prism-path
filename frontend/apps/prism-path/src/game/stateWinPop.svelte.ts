// The win-line VALUE pop's shared state. WinLines drives it frame-by-frame; WinValuePop
// renders it. Split from WinLines so the pop can mount ABOVE the multiplier-badge layer
// while the ribbon stays below it (z: symbols < trail < ribbons < badges < value pop).
export const POP_FONT = 40;
export const MULT_FONT = 32;
export const MULT_Y = 40; // the xN sits under the value before merging into it

export const stateWinPop = $state({
	x: 0,
	y: 0,
	scale: 0,
	alpha: 0,
	multY: MULT_Y,
	multScale: 0,
	multAlpha: 0,
	label: '',
	multLabel: '',
});
