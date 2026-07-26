<script lang="ts">
	import { Graphics } from 'pixi-svelte';

	import { paletteAt, lerpColor } from '../game/motion';
	import { TRAIL_FLOW_HZ } from '../game/trailBeam';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	// The STICKY dragon's eyes are PURPOSEFULLY keyed out of the art (enclosed alpha holes):
	// this fill renders BEHIND the sprite, so the sockets mask it to crisp crystal-cut eyes.
	// The colour is the WILD-PATH language — the same palette, streaming at the same
	// TRAIL_FLOW_HZ phase as the beam (paletteAt(u - phase)), just compressed across the
	// socket so the eye reads richly multicolour, with a white-hot core for brightness.
	//
	// Socket geometry measured from the NATIVE (UP-facing) texture's alpha holes (256-space ->
	// symbol-local at the 0.94 special ratio); re-measure if the art is replaced.
	const EYES_UP = [
		{ x: -12.17, y: -14.05, w: 3.72, h: 5.82 },
		{ x: 11.7, y: -14.08, w: 3.76, h: 5.7 },
	] as const;

	type Direction = 'up' | 'down' | 'left' | 'right';

	// screen-space transforms of the up-art socket positions for each rotated variant
	// (90° rotations also swap the socket's w/h)
	const PLACE: Record<Direction, (e: { x: number; y: number; w: number; h: number }) => { x: number; y: number; w: number; h: number }> = {
		up: (e) => e,
		down: (e) => ({ x: -e.x, y: -e.y, w: e.w, h: e.h }),
		right: (e) => ({ x: -e.y, y: e.x, w: e.h, h: e.w }),
		left: (e) => ({ x: e.y, y: -e.x, w: e.h, h: e.w }),
	};

	// unit vector of the facing direction — the gradient streams along it, like the path
	const AXIS: Record<Direction, { x: number; y: number }> = {
		down: { x: 0, y: 1 },
		up: { x: 0, y: -1 },
		right: { x: 1, y: 0 },
		left: { x: -1, y: 0 },
	};

	const SLICES = 5;
	const HUE_SPAN = 0.45; // palette fraction across one eye — compressed = richly multicolour

	type Props = {
		x?: number;
		y?: number;
		direction?: Direction;
	};

	const props: Props = $props();
	const dir = $derived(props.direction ?? 'up');

	$effect(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});
</script>

<Graphics
	x={props.x ?? 0}
	y={props.y ?? 0}
	draw={(g) => {
		const phase = trailClock.t * TRAIL_FLOW_HZ; // same stream clock as the wild path
		const breathe = 0.92 + 0.08 * Math.sin(phase * Math.PI * 1.6); // beam's breath
		const ax = AXIS[dir];
		for (const eyeUp of EYES_UP) {
			const e = PLACE[dir](eyeUp);
			const along = ax.x !== 0 ? e.w : e.h; // socket extent along the facing axis
			// gradient slices streaming toward the facing direction (beam formula: u - phase)
			for (let i = 0; i < SLICES; i++) {
				const s = i / (SLICES - 1) - 0.5; // -0.5 .. +0.5 along the axis
				const col = paletteAt(s * HUE_SPAN - phase);
				g.ellipse(e.x + ax.x * s * along * 0.8, e.y + ax.y * s * along * 0.8, e.w * 0.62, e.h * 0.58).fill({
					color: lerpColor(col, 0xffffff, 0.12 + 0.1 * breathe), // lifted = brighter than the beam
					alpha: 1,
				});
			}
			// white-hot core, breathing on the beam clock
			g.ellipse(e.x, e.y, e.w * 0.26, e.h * 0.24).fill({
				color: lerpColor(paletteAt(-phase), 0xffffff, 0.8),
				alpha: 0.75 + 0.25 * breathe,
			});
		}
	}}
/>
