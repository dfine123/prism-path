<script lang="ts">
	// A wild cell created by a Prism Beast — the PERSISTENT continuation of the dragon's
	// in-flight ribbon. Rendering comes from the SHARED beam renderer (game/trailBeam.ts) on
	// the shared absolute clock, so the hand-off from flight to resting cell is
	// pixel-identical: it lands at the flight's heat (TRAIL_HOT_FLIGHT) and settles to rest.
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { EASE, clamp01 } from '../game/motion';
	import { stateFx } from '../game/stateFx.svelte';
	import { drawTrailBeam, TRAIL_FLOW_HZ, TRAIL_HOT_FLIGHT } from '../game/trailBeam';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import type { SymbolState } from '../game/types';

	type Props = {
		direction: 'up' | 'down' | 'left' | 'right';
		state: SymbolState;
		oncomplete?: () => void;
	};
	const props: Props = $props();

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});

	// The symbol pipeline awaits oncomplete. On WIN the beam brightens and holds for the
	// same beat as the sprite breath so an all-wild line still paces the sequence
	// (scaled-time so click-to-skip accelerates it too).
	const WIN_HOLD_MS = 460;
	$effect(() => {
		if (props.state === 'win') {
			let lastT = performance.now();
			let el = 0;
			let raf = 0;
			let done = false;
			const frame = () => {
				const t = performance.now();
				el += (t - lastT) * stateFx.winSpeed;
				lastT = t;
				if (el >= WIN_HOLD_MS) {
					if (!done) {
						done = true;
						props.oncomplete?.();
					}
					return;
				}
				raf = requestAnimationFrame(frame);
			};
			raf = requestAnimationFrame(frame);
			return () => cancelAnimationFrame(raf);
		}
		props.oncomplete?.();
	});

	const horizontal = $derived(props.direction === 'left' || props.direction === 'right');
	const flowSign = $derived(props.direction === 'left' || props.direction === 'up' ? -1 : 1);

	// ACTIVATION settle-in: starts at EXACTLY the flight ribbon's heat and flows down to
	// rest — the ribbon->cell hand-off never snaps.
	const born = performance.now();

	// WIN boost: pops IN fast (impact) and RETRACTS slowly (settle) — never a step.
	let boost = $state(1);
	$effect(() => {
		const target = props.state === 'win' ? 1.4 : 1;
		const from = boost;
		if (Math.abs(target - from) < 0.005) return;
		const rising = target > from;
		const dur = rising ? 150 : 380;
		const ease = rising ? EASE.impact : EASE.settle;
		const start = performance.now();
		let raf = 0;
		const frame = () => {
			const u = Math.min(1, (performance.now() - start) / dur);
			boost = from + (target - from) * ease(u);
			if (u < 1) raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});
</script>

<Graphics
	blendMode="add"
	draw={(g) => {
		const phase = trailClock.t * TRAIL_FLOW_HZ;
		const settleIn =
			1 + (TRAIL_HOT_FLIGHT - 1) * (1 - EASE.settle(clamp01((performance.now() - born) / 450)));
		drawTrailBeam(g, {
			cx: 0,
			cy: 0,
			horizontal,
			flowSign,
			phase,
			hot: boost * settleIn,
		});
	}}
/>
