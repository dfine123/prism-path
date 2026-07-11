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
	import { SYMBOL_SIZE } from '../game/constants';
	import { paletteAt } from '../game/motion';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	const context = getContext();

	let markers = $state<Position[]>([]);

	$effect(() => {
		if (markers.length > 0) {
			acquireTrailClock();
			return releaseTrailClock;
		}
	});

	context.eventEmitter.subscribeOnMount({
		stickyMarkerAdd: ({ position }) => {
			if (!markers.some((m) => m.reel === position.reel && m.row === position.row)) {
				markers = [...markers, position];
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
			for (let i = 0; i < markers.length; i++) {
				const m = markers[i];
				// fixed GRID coords (markers belong to the square, not the scrolling symbols);
				// m.row is the padded index -> visible centre y = (row - 0.5) * SYMBOL_SIZE
				const x = getSymbolX(m.reel);
				const y = (m.row - 0.5) * SYMBOL_SIZE;
				const breathe = 0.8 + 0.2 * Math.sin(t * Math.PI * 1.8 + i * 1.3);
				const s = SYMBOL_SIZE * (0.94 + 0.02 * Math.sin(t * Math.PI * 1.8 + i * 1.3));
				const col = paletteAt(t * 0.35 + i * 0.21);
				// soft outer bloom -> saturated border -> crisp inner edge
				g.roundRect(x - s / 2, y - s / 2, s, s, 14).stroke({ width: 11, color: col, alpha: 0.18 * breathe });
				g.roundRect(x - s / 2, y - s / 2, s, s, 14).stroke({ width: 4.5, color: col, alpha: 0.85 * breathe });
				g.roundRect(x - s / 2, y - s / 2, s, s, 14).stroke({ width: 1.5, color: 0xffffff, alpha: 0.55 * breathe });
				// corner sparks (one per corner, twinkling out of phase)
				const h = s / 2;
				const corners = [
					[x - h, y - h],
					[x + h, y - h],
					[x + h, y + h],
					[x - h, y + h],
				];
				for (let k = 0; k < 4; k++) {
					const tw = (Math.sin(t * Math.PI * 3 + i * 1.7 + k * 1.9) + 1) / 2;
					g.circle(corners[k][0], corners[k][1], 2 + 2.4 * tw).fill({ color: 0xffffff, alpha: 0.3 + 0.45 * tw });
				}
			}
		}}
	/>
{/if}
