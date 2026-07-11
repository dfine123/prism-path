<script lang="ts">
	// A wild cell created by a Prism Beast. NOT a dragon head — an animated prismatic light
	// trail filling the cell along the beast's fire axis. The gradient wraps exactly once per
	// cell, so adjacent trail cells tile into ONE continuous streaming beam across the line.
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { SYMBOL_SIZE } from '../game/constants';
	import { paletteAt } from '../game/motion';
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

	// the symbol pipeline awaits oncomplete for land/win states (sprites resolve instantly)
	onMount(() => props.oncomplete?.());
	$effect(() => {
		props.state;
		props.oncomplete?.();
	});

	const horizontal = $derived(props.direction === 'left' || props.direction === 'right');
	// gradient streams IN the fire direction
	const flowSign = $derived(props.direction === 'left' || props.direction === 'up' ? -1 : 1);
	const winBoost = $derived(props.state === 'win' ? 1.4 : 1);
</script>

<Graphics
	blendMode="add"
	draw={(g) => {
		const phase = trailClock.t * FLOW_HZ;
		const L = SYMBOL_SIZE;
		const breathe = 0.92 + 0.08 * Math.sin(phase * Math.PI * 1.6);
		const W = SYMBOL_SIZE * W_BASE * (1 + (winBoost - 1) * 0.35);
		const aMul = breathe * winBoost;
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
