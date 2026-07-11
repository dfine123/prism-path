// Shared animation clock for the persistent wild-trail cells: ONE rAF drives every cell so the
// whole line streams in the same phase (seamless across cells) and the loop stops when no trail
// cells are mounted. Components: acquire on mount, release on destroy, read trailClock.t in draw.
let users = 0;
let raf = 0;

export const trailClock = $state({ t: 0 });

const tick = () => {
	trailClock.t = performance.now() / 1000;
	raf = users > 0 ? requestAnimationFrame(tick) : 0;
};

export const acquireTrailClock = () => {
	users++;
	if (!raf) raf = requestAnimationFrame(tick);
};

export const releaseTrailClock = () => {
	users = Math.max(0, users - 1);
	if (!users && raf) {
		cancelAnimationFrame(raf);
		raf = 0;
	}
};
