// Presentation FX state. winSpeed multiplies the win-presentation clocks (1 = normal).
// A click during the line sequence is the player asking to skip — the winInfo handler
// raises this substantially and every paced surface (line lifecycle, symbol breath,
// wild hold) consumes it via scaled-time accumulation.
//
// boardScale / boardNudgeY are the BOARD-FEEL channels: every BoardContainer instance
// reads them, so the static and animate layers move as one. Drive them ONLY through
// boardBreathe() / boardSlam() below (single rAF per channel; re-triggers restart cleanly).
export const stateFx = $state({ winSpeed: 1, boardScale: 1, boardNudgeY: 0 });

// A breath as the reels launch, in four beats — GATHER, SWELL, FALL, CATCH — so the eye
// catches it against the reel motion AND the return reads as WEIGHT: a quick contraction,
// an easy swell to the peak, then an ACCELERATING fall back home (mass, not float) that
// lands with a tiny compression below rest before settling.
const BREATH_MS = 620;
const BREATH_DIP = 0.006; // gather contraction
const BREATH_RISE = 0.024; // swell peak
const BREATH_UNDER = 0.005; // landing compression below rest
const BREATH_DIP_END = 0.15; // beat boundaries (fractions of the breath)
const BREATH_PEAK_U = 0.45;
const BREATH_LAND_U = 0.85;
const BREATH_FALL_POW = 2.2; // >1 = the fall accelerates; raise for an even heavier drop
const BREATH_REFRACTORY_MS = 700; // one breath per launch beat (press + reveal fire close together)
let breathRaf = 0;
let breathLastStart = -Infinity;

export const boardBreathe = () => {
	if (performance.now() - breathLastStart < BREATH_REFRACTORY_MS) return;
	breathLastStart = performance.now();
	cancelAnimationFrame(breathRaf);
	const start = performance.now();
	const frame = () => {
		const u = Math.min(1, (performance.now() - start) / BREATH_MS);
		if (u < BREATH_DIP_END) {
			// gather: ease down to the dip
			stateFx.boardScale = 1 - BREATH_DIP * Math.sin((u / BREATH_DIP_END) * Math.PI * 0.5);
		} else if (u < BREATH_PEAK_U) {
			// swell: easy rise from the dip, cresting weightlessly at the peak (slope -> 0)
			const r = (u - BREATH_DIP_END) / (BREATH_PEAK_U - BREATH_DIP_END);
			stateFx.boardScale =
				1 - BREATH_DIP + (BREATH_RISE + BREATH_DIP) * Math.sin(r * Math.PI * 0.5);
		} else if (u < BREATH_LAND_U) {
			// fall: accelerate from the crest down PAST rest to the compression point
			const r = (u - BREATH_PEAK_U) / (BREATH_LAND_U - BREATH_PEAK_U);
			stateFx.boardScale =
				1 + BREATH_RISE - (BREATH_RISE + BREATH_UNDER) * Math.pow(r, BREATH_FALL_POW);
		} else {
			// catch: quick decelerating recovery from the compression up to rest
			const r = (u - BREATH_LAND_U) / (1 - BREATH_LAND_U);
			stateFx.boardScale = 1 - BREATH_UNDER * (1 - Math.sin(r * Math.PI * 0.5));
		}
		if (u < 1) {
			breathRaf = requestAnimationFrame(frame);
		} else {
			stateFx.boardScale = 1;
		}
	};
	breathRaf = requestAnimationFrame(frame);
};

// Directional board IMPULSES — one damped-spring channel drives boardNudgeX/Y.
// boardSlam: the dragon-lands thud (sharp, vertical, quarter-second).
// boardRubberBand: the dragon PUSHING PAST the board edge drags the board with it a few
// px in its exit direction, then the board springs back past rest and settles — a soft
// rubber-band, slower and springier than the slam.
let impulseRaf = 0;

const boardImpulse = (dx: number, dy: number, amp: number, ms: number, decay: number, cycles: number) => {
	cancelAnimationFrame(impulseRaf);
	const len = Math.hypot(dx, dy) || 1;
	const ux = dx / len;
	const uy = dy / len;
	const start = performance.now();
	const frame = () => {
		const u = Math.min(1, (performance.now() - start) / ms);
		const k = amp * Math.exp(-decay * u) * Math.sin(u * Math.PI * cycles);
		stateFx.boardNudgeX = ux * k;
		stateFx.boardNudgeY = uy * k;
		if (u < 1) {
			impulseRaf = requestAnimationFrame(frame);
		} else {
			stateFx.boardNudgeX = 0;
			stateFx.boardNudgeY = 0;
		}
	};
	impulseRaf = requestAnimationFrame(frame);
};

export const boardSlam = (strength = 1) => boardImpulse(0, 1, 4 * strength, 260, 4.2, 3);

export const boardRubberBand = (dx: number, dy: number, strength = 1) =>
	boardImpulse(dx, dy, 7 * strength, 520, 3.1, 2.2);
