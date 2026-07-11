<script lang="ts">
	// Prism light-curtain transition (replaces the template Spine curtain): a wall of dark
	// crystal swept across the screen behind a prismatic leading edge — fully covers at the
	// midpoint (the swap hides under it), then releases. Committed wipe, never a hard cut.
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { EASE, clamp01, lerp, paletteAt } from '../game/motion';

	type Props = {
		oncomplete: () => void;
		oncovered?: () => void; // fired ONCE at full cover — swap the scene behind the curtain
	};
	const props: Props = $props();
	const context = getContext();

	const DURATION_MS = 1050;

	let t01 = $state(0); // 0..1 sweep progress
	let done = false;
	let coveredFired = false;

	onMount(() => {
		const start = performance.now();
		let raf = 0;
		const frame = () => {
			const el = performance.now() - start;
			t01 = clamp01(el / DURATION_MS);
			// the band fully covers the screen for eased progress ~[0.435, 0.565]
			if (!coveredFired && easeInOut(t01) >= 0.5) {
				coveredFired = true;
				props.oncovered?.();
			}
			if (el < DURATION_MS) {
				raf = requestAnimationFrame(frame);
			} else if (!done) {
				done = true;
				props.oncomplete();
			}
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	// ease the sweep: fast into cover, releases with a settle
	const easeInOut = (u: number) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2);
</script>

<Graphics
	draw={(g) => {
		const c = context.stateLayoutDerived.canvasSizes();
		const W = c.width;
		const H = c.height;
		// a band wider than the screen sweeps through: fully covers EXACTLY at the midpoint
		// (the swap hides under it) and is fully clear at both ends — no pop on unmount.
		const BW = W * 1.3;
		const bx = lerp(-BW, W, easeInOut(t01)); // band spans [bx, bx + BW]
		g.rect(bx, -H * 0.1, BW, H * 1.2).fill({ color: 0x0b0814, alpha: 0.985 });
		// prismatic LEADING edge (right side, sweeping in) + hot core
		const EDGE = W * 0.05;
		const lead = bx + BW;
		for (let i = 0; i < 6; i++) {
			const col = paletteAt(i / 6 - t01 * 1.2);
			g.rect(lead + (i / 6) * EDGE, -H * 0.1, EDGE / 6 + 2, H * 1.2).fill({ color: col, alpha: 0.5 - i * 0.06 });
		}
		g.rect(lead - 3, -H * 0.1, 6, H * 1.2).fill({ color: 0xffffff, alpha: 0.85 });
		// prismatic TRAILING edge (left side, releasing)
		for (let i = 0; i < 6; i++) {
			const col = paletteAt(i / 6 + t01 * 1.2);
			g.rect(bx - (i / 6) * EDGE - EDGE / 6, -H * 0.1, EDGE / 6 + 2, H * 1.2).fill({ color: col, alpha: 0.45 - i * 0.055 });
		}
		g.rect(bx - 3, -H * 0.1, 6, H * 1.2).fill({ color: 0xffffff, alpha: 0.7 });
		// shimmer motes on the curtain surface
		for (let k = 0; k < 9; k++) {
			const sy = ((k * 0.117 + t01 * 0.35) % 1) * H;
			const sx = bx + BW * (0.15 + (k % 3) * 0.28);
			const tw = (Math.sin(t01 * Math.PI * 6 + k * 2.1) + 1) / 2;
			g.circle(sx, sy, 1.5 + 2.5 * tw).fill({ color: 0xffffff, alpha: 0.2 + 0.4 * tw });
		}
	}}
/>
