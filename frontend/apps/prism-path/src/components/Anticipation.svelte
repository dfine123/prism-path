<script lang="ts">
	// Scatter anticipation — a pulsing prism light column over the anticipated reel
	// (replaces the template Spine). Bloom in -> pulse while the reel lingers -> release
	// when it stops. The lingering reel IS the dopamine; this just points the eye at it.
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import type { Reel } from '../game/stateGame.svelte';
	import { REEL_PADDING, SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { EASE, clamp01, paletteAt } from '../game/motion';

	type Props = {
		reel: Reel;
		oncomplete: () => void;
	};

	const props: Props = $props();
	const context = getContext();

	let t = $state(0);
	let outStart = $state<number | null>(null);
	let born = 0;
	let finished = false;

	onMount(() => {
		born = performance.now();
		let raf = 0;
		const frame = () => {
			t = performance.now();
			if (outStart !== null && t - outStart > 320 && !finished) {
				finished = true;
				props.oncomplete();
				return;
			}
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	$effect(() => {
		if (props.reel.reelState.motion === 'stopped' && outStart === null) {
			outStart = performance.now();
		}
	});

	const envelope = $derived.by(() => {
		const inE = EASE.load(clamp01((t - born) / 260));
		const outE = outStart === null ? 1 : 1 - EASE.collapse(clamp01((t - outStart) / 320));
		return inE * outE;
	});

	const colX = $derived(
		context.stateGameDerived.boardLayout().x -
			context.stateGameDerived.boardLayout().width * 0.5 +
			(props.reel.reelIndex + REEL_PADDING) * CELL_W,
	);
	const colY = $derived(context.stateGameDerived.boardLayout().y);
</script>

{#if envelope > 0.01}
	<Graphics
		blendMode="add"
		x={colX}
		y={colY}
		draw={(g) => {
			const secs = t / 1000;
			const H = context.stateGameDerived.boardLayout().height * 1.02;
			const pulse = 0.75 + 0.25 * Math.sin(secs * Math.PI * 2.4);
			const W = CELL_W * 0.98;
			const col = paletteAt(secs * 0.3);
			// column glow: halo -> body -> hot edges
			g.rect(-W * 0.62, -H / 2, W * 1.24, H).fill({ color: col, alpha: 0.05 * envelope * pulse });
			g.rect(-W / 2, -H / 2, W, H).fill({ color: col, alpha: 0.1 * envelope * pulse });
			g.rect(-W / 2 - 2, -H / 2, 4, H).fill({ color: 0xffffff, alpha: 0.4 * envelope * pulse });
			g.rect(W / 2 - 2, -H / 2, 4, H).fill({ color: 0xffffff, alpha: 0.4 * envelope * pulse });
			// rising sparks
			for (let k = 0; k < 6; k++) {
				const u = ((k * 0.19 + secs * 0.5) % 1);
				const sy = H / 2 - u * H;
				const sx = Math.sin(secs * 2.2 + k * 1.9) * W * 0.3;
				const tw = (Math.sin(secs * Math.PI * 4 + k * 2.1) + 1) / 2;
				g.circle(sx, sy, 1.6 + 2 * tw).fill({ color: 0xffffff, alpha: (0.25 + 0.4 * tw) * envelope * u });
			}
		}}
	/>
{/if}
