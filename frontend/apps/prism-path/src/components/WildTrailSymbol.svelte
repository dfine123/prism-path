<script lang="ts">
	// A wild cell created by a Prism Beast. NOT a dragon head — an animated prismatic light
	// trail filling the cell along the beast's fire axis. The gradient wraps exactly once per
	// cell, so adjacent trail cells tile into ONE continuous streaming beam across the line.
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { EASE, clamp01, paletteAt } from '../game/motion';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import type { SymbolState } from '../game/types';

	type Props = {
		direction: 'up' | 'down' | 'left' | 'right';
		state: SymbolState;
		oncomplete?: () => void;
	};
	const props: Props = $props();

	// ---- feel tunables ----
	const FLOW_HZ = 0.55; // stream speed of the gradient along the line
	const W_BASE = 0.44; // beam width (x symbol)
	const SEGS = 6;

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});

	// The symbol pipeline awaits oncomplete. On WIN the trail brightens (winBoost) and holds
	// for the same beat as the sprite breath so an all-wild line still paces the sequence.
	const WIN_HOLD_MS = 460;
	$effect(() => {
		if (props.state === 'win') {
			const id = setTimeout(() => props.oncomplete?.(), WIN_HOLD_MS);
			return () => clearTimeout(id);
		}
		props.oncomplete?.();
	});

	const horizontal = $derived(props.direction === 'left' || props.direction === 'right');
	// gradient streams IN the fire direction
	const flowSign = $derived(props.direction === 'left' || props.direction === 'up' ? -1 : 1);

	// ACTIVATION settle-in: the cell lands HOT (the ribbon's energy) and flows down to its
	// resting glow — never a snap.
	const born = performance.now();

	// WIN boost is a smoothed value: pops IN fast (impact) and RETRACTS slowly (settle) —
	// a step function here reads as the cell "snapping back".
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
		const phase = trailClock.t * FLOW_HZ;
		// beam spans the FULL cell along the fire axis (cells are rectangular) so adjacent
		// trail cells keep tiling into one continuous line
		const L = horizontal ? CELL_W : SYMBOL_SIZE;
		const breathe = 0.92 + 0.08 * Math.sin(phase * Math.PI * 1.6);
		// hot on activation -> settles to rest; win boost eases in AND out
		const settleIn = 1 + 0.6 * (1 - EASE.settle(clamp01((performance.now() - born) / 450)));
		const hot = boost * settleIn;
		const W = SYMBOL_SIZE * W_BASE * (1 + (hot - 1) * 0.35);
		const aMul = breathe * hot;
		for (let i = 0; i < SEGS; i++) {
			const u0 = i / SEGS;
			const u1 = (i + 1) / SEGS;
			const mid = (u0 + u1) / 2;
			const col = paletteAt(flowSign * mid - phase);
			// subtle traveling width ripple so the beam feels alive, not printed
			const w = W * (1 + 0.06 * Math.sin((flowSign * mid - phase) * Math.PI * 2));
			const p0 = -L / 2 + u0 * L - 0.5;
			const seg = L / SEGS + 1;
			if (horizontal) {
				g.rect(p0, -w * 0.9, seg, w * 1.8).fill({ color: col, alpha: 0.1 * aMul }); // halo
				g.rect(p0, -w * 0.5, seg, w).fill({ color: col, alpha: 0.32 * aMul }); // body
				g.rect(p0, -w * 0.16, seg, w * 0.32).fill({ color: 0xffffff, alpha: 0.3 * aMul }); // core
			} else {
				g.rect(-w * 0.9, p0, w * 1.8, seg).fill({ color: col, alpha: 0.1 * aMul });
				g.rect(-w * 0.5, p0, w, seg).fill({ color: col, alpha: 0.32 * aMul });
				g.rect(-w * 0.16, p0, w * 0.32, seg).fill({ color: 0xffffff, alpha: 0.3 * aMul });
			}
		}
		// drifting sparkle motes riding the stream
		for (let k = 0; k < 3; k++) {
			const u = (((k * 0.34 + flowSign * phase * 0.45) % 1) + 1) % 1;
			const p = -L / 2 + u * L;
			const tw = (Math.sin(phase * Math.PI * 5 + k * 2.1) + 1) / 2;
			const wob = Math.sin(phase * Math.PI * 2.6 + k * 1.7) * W * 0.3;
			const px = horizontal ? p : wob;
			const py = horizontal ? wob : p;
			g.circle(px, py, 1.6 + 1.5 * tw).fill({ color: 0xffffff, alpha: (0.2 + 0.45 * tw) * aMul });
		}
	}}
/>
