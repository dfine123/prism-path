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
	{ key: 'board1', label: '1 Crystal', scaleW: 1.18, scaleH: 1.19 },
	{ key: 'board2', label: '2 Gemstud', scaleW: 1.18, scaleH: 1.19 },
	{ key: 'board3', label: '3 Gold', scaleW: 1.18, scaleH: 1.19 },
	{ key: 'board4', label: '4 Minimal', scaleW: 1.18, scaleH: 1.19 },
];

export const stateDev = $state({
	frameIndex: 0,
	// live-tunable copy of the selected option's fit
	scaleW: FRAME_OPTIONS[0].scaleW,
	scaleH: FRAME_OPTIONS[0].scaleH,
	panelOpen: true,
});

export const selectFrame = (index: number) => {
	stateDev.frameIndex = index;
	stateDev.scaleW = FRAME_OPTIONS[index].scaleW;
	stateDev.scaleH = FRAME_OPTIONS[index].scaleH;
};
