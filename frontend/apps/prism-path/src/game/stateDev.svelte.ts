// DEV-ONLY state: board-frame candidate picker (remove once a frame is locked).
// The panel (DevFramePanel.svelte) toggles candidates and live-nudges the fit so each
// option can be judged properly sized on the real board.
export type FrameOption = {
	key: string;
	label: string;
	scaleW: number; // frame width  = board width  * scaleW
	scaleH: number; // frame height = board height * scaleH
	offX?: number; // render px — aligns an off-centre art opening with the board centre
	offY?: number;
};

export const FRAME_OPTIONS: FrameOption[] = [
	{ key: 'prismFrameEdge', label: 'Old', scaleW: 1.14, scaleH: 1.15 },
	// CHOSEN: crystal v2 (board_42, LANDSCAPE — the board conforms to its opening aspect
	// 1.2155 via rectangular cells). Fit from the measured opening (79.8% x 76.7% of the
	// art) so the opening = board minus a 4px lip per side; offsets align the art's
	// slightly off-centre opening with the board centre.
	{ key: 'board1', label: '1 Crystal', scaleW: 1.236, scaleH: 1.282, offX: 1.5, offY: -3.6 },
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
