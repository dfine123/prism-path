<script lang="ts" module>
	import type { Position } from '../game/types';

	// STICKY DRAGON markers (placeholder until a dedicated sticky symbol exists): the square a
	// sticky dragon claims gets a persistent GLOWING BORDER for the rest of the feature. The
	// dragon itself animates like any other (full travel) — the border is the sticky signal,
	// and the dragon re-lands on the marked square every spin.
	export type EmitterEventStickyMarkers =
		| { type: 'stickyMarkerAdd'; position: Position }
		| { type: 'stickyMarkerClear' };
</script>

<script lang="ts">
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { getSymbolX } from '../game/utils';
	import { SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { paletteAt, clamp01 } from '../game/motion';
	import { stateWinPop } from '../game/stateWinPop.svelte';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	const context = getContext();

	let markers = $state<(Position & { bornAt: number })[]>([]);

	$effect(() => {
		if (markers.length > 0) {
			acquireTrailClock();
			return releaseTrailClock;
		}
	});

	context.eventEmitter.subscribeOnMount({
		stickyMarkerAdd: ({ position }) => {
			if (!markers.some((m) => m.reel === position.reel && m.row === position.row)) {
				markers = [...markers, { ...position, bornAt: performance.now() / 1000 }];
			}
		},
		stickyMarkerClear: () => {
			markers = [];
		},
	});
</script>

{#if markers.length > 0}
	<Graphics
		blendMode="add"
		draw={(g) => {
			const t = trailClock.t;
			// LEGIBILITY GUARD: while a win VALUE POP is on stage, the ring's additive glow
			// washes out the thin glyphs (it reads as sitting ON TOP of the number even
			// though it paints below) — so the whole marker ducks to a whisper and swells
			// back when the pop leaves
			const duck = 1 - 0.8 * clamp01(stateWinPop.alpha);
			for (let i = 0; i < markers.length; i++) {
				const m = markers[i];
				// fixed GRID coords (markers belong to the square, not the scrolling symbols);
				// m.row is the padded index -> visible centre y = (row - 0.5) * SYMBOL_SIZE
				const x = getSymbolX(m.reel);
				const y = (m.row - 0.5) * SYMBOL_SIZE;
				// BIRTH BLOOM: the claim moment ignites — the ring blooms in from a hot
				// oversized flash and settles into the idle breathe (was a hard pop-in)
				const age = clamp01((t - m.bornAt) / 0.34);
				const birthScale = 1 + 0.16 * (1 - age) * (1 - age);
				const birthHot = 1 + 2.2 * (1 - age);
				const breathe = (0.8 + 0.2 * Math.sin(t * Math.PI * 1.8 + i * 1.3)) * Math.min(birthHot, 1.9);
				const pulse = (0.94 + 0.02 * Math.sin(t * Math.PI * 1.8 + i * 1.3)) * birthScale;
				const w = CELL_W * pulse; // rectangular cells
				const h2 = SYMBOL_SIZE * pulse;
				const col = paletteAt(t * 0.35 + i * 0.21);
				// soft outer bloom -> saturated border -> crisp inner edge
				g.roundRect(x - w / 2, y - h2 / 2, w, h2, 14).stroke({ width: 11, color: col, alpha: 0.18 * breathe * duck });
				g.roundRect(x - w / 2, y - h2 / 2, w, h2, 14).stroke({ width: 4.5, color: col, alpha: 0.85 * breathe * duck });
				g.roundRect(x - w / 2, y - h2 / 2, w, h2, 14).stroke({ width: 1.5, color: 0xffffff, alpha: 0.55 * breathe * duck });
				// corner sparks (one per corner, twinkling out of phase)
				const corners = [
					[x - w / 2, y - h2 / 2],
					[x + w / 2, y - h2 / 2],
					[x + w / 2, y + h2 / 2],
					[x - w / 2, y + h2 / 2],
				];
				for (let k = 0; k < 4; k++) {
					const tw = (Math.sin(t * Math.PI * 3 + i * 1.7 + k * 1.9) + 1) / 2;
					g.circle(corners[k][0], corners[k][1], 2 + 2.4 * tw).fill({ color: 0xffffff, alpha: (0.3 + 0.45 * tw) * duck });
				}
			}
		}}
	/>
{/if}
