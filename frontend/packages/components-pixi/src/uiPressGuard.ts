// UI-press guard: Button marks every pointerdown that lands ON a UI control, so
// window-level "press anywhere" listeners (e.g. the board's quick-stop slam) can tell a
// console press apart from a board press. Pixi pointer events dispatch during the same
// native event as the window listener, and the canvas listener runs first — so the mark
// is already set when the window handler asks.
let lastUiPressAt = -Infinity;

export const markUiPress = () => {
	lastUiPressAt = performance.now();
};

/** True if a UI control handled a pointerdown within the last `windowMs` (default 80). */
export const wasRecentUiPress = (windowMs = 80) => performance.now() - lastUiPressAt < windowMs;
