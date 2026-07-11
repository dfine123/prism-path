// DEV-ONLY state: board-frame candidate picker (remove once a frame is locked).
// The panel (DevFramePanel.svelte) toggles candidates and live-nudges the fit so each
// option can be judged properly sized on the real board.
export type FrameOption = {
	key: string;
	label: string;
	scaleW: number; // frame width  = board width  * scaleW
	scaleH: number; // frame height = board height * scaleH
};

export const FRAME_OPTIONS: FrameOption[] = [
	{ key: 'prismFrameEdge', label: 'Current', scaleW: 1.14, scaleH: 1.15 },
	// CHOSEN: crystal. Fit measured from the art's inner opening (79.8% x 73.3% of the
	// image) so the opening = board minus a 4px lip per side -> 1.233 x 1.342.
	{ key: 'board1', label: '1 Crystal', scaleW: 1.233, scaleH: 1.342 },
	{ key: 'board2', label: '2 Gemstud', scaleW: 1.18, scaleH: 1.19 },
	{ key: 'board3', label: '3 Gold', scaleW: 1.18, scaleH: 1.19 },
	{ key: 'board4', label: '4 Minimal', scaleW: 1.18, scaleH: 1.19 },
];

const BOOT_FRAME = 1; // crystal (user-chosen)

export const stateDev = $state({
	frameIndex: BOOT_FRAME,
	// live-tunable copy of the selected option's fit
	scaleW: FRAME_OPTIONS[BOOT_FRAME].scaleW,
	scaleH: FRAME_OPTIONS[BOOT_FRAME].scaleH,
	panelOpen: true,
});

export const selectFrame = (index: number) => {
	stateDev.frameIndex = index;
	stateDev.scaleW = FRAME_OPTIONS[index].scaleW;
	stateDev.scaleH = FRAME_OPTIONS[index].scaleH;
};
