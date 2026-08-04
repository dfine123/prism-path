<script lang="ts">
	// CUT CRYSTAL PLAQUE — the shared celebration/panel surface (win boxes, FS intro/outro,
	// counter chip). One material, straight from the game's established language:
	// - silhouette: chamfered gem-cut octagon (not a generic rounded rect)
	// - surface: the BOARD GLASS recipe (deep violet, top-light sheen, inner lip shade)
	// - border: the board's engraved groove (dark undercut + lavender light core) with a
	//   TRAVELING prism shimmer running the perimeter (the trail-flow made architectural)
	// - facet gems: twinkling diamonds at the cut vertices (the marker corner-spark motif)
	// `accent` pins the light to one tier colour (win tiers / gold at max); omitted, the
	// shimmer cycles the palette like the sticky markers do.
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { paletteAt } from '../game/motion';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	type Props = {
		width: number;
		height: number;
		radius?: number; // legacy name — maps to the chamfer cut size
		chamfer?: number;
		accent?: number; // fixed light colour; omit for the cycling prism ramp
		opaque?: boolean; // win boxes: fully solid plate (nothing may ghost through)
		children?: Snippet;
	};
	const props: Props = $props();
	const cut = $derived(
		props.chamfer ?? props.radius ?? Math.min(26, Math.min(props.width, props.height) * 0.16),
	);

	// chamfered octagon, centred on origin
	const octagon = (w: number, h: number, c: number): number[] => {
		const w2 = w / 2;
		const h2 = h / 2;
		return [
			-w2 + c, -h2,
			w2 - c, -h2,
			w2, -h2 + c,
			w2, h2 - c,
			w2 - c, h2,
			-w2 + c, h2,
			-w2, h2 - c,
			-w2, -h2 + c,
		];
	};

	// point at arc-length s along the closed outline (for the traveling shimmer)
	const perimeterPoint = (pts: number[], s: number) => {
		const n = pts.length / 2;
		for (let i = 0; i < n; i++) {
			const x0 = pts[i * 2];
			const y0 = pts[i * 2 + 1];
			const x1 = pts[((i + 1) % n) * 2];
			const y1 = pts[((i + 1) % n) * 2 + 1];
			const len = Math.hypot(x1 - x0, y1 - y0);
			if (s <= len) {
				const u = len > 0 ? s / len : 0;
				return { x: x0 + (x1 - x0) * u, y: y0 + (y1 - y0) * u };
			}
			s -= len;
		}
		return { x: pts[0], y: pts[1] };
	};

	const perimeterLength = (pts: number[]) => {
		const n = pts.length / 2;
		let total = 0;
		for (let i = 0; i < n; i++) {
			total += Math.hypot(
				pts[((i + 1) % n) * 2] - pts[i * 2],
				pts[((i + 1) % n) * 2 + 1] - pts[i * 2 + 1],
			);
		}
		return total;
	};

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});
</script>

<!-- plate: board-glass surface (normal blend — real material, not light) -->
<Graphics
	draw={(g) => {
		const w = props.width;
		const h = props.height;
		const pts = octagon(w, h, cut);
		// glass base — denser than the board panel (text must read over the dim veil).
		// opaque mode: a WIN BOX is a solid plate — shards erupting behind it must be
		// fully occluded, so the base paints twice (alpha stacking leaves no bleed).
		if (props.opaque) {
			g.poly(pts).fill({ color: 0x140b24, alpha: 1 });
			g.poly(pts).fill({ color: 0x140b24, alpha: 1 });
		} else {
			g.poly(pts).fill({ color: 0x140b24, alpha: 0.93 });
		}
		// top-light sheen: stepped strips fading out by ~1/3 down (imperceptible deltas)
		const STEPS = 6;
		const sheenH = h * 0.34;
		const stepH = sheenH / STEPS;
		for (let s = 0; s < STEPS; s++) {
			g.rect(-w / 2 + cut + 6, -h / 2 + 3 + s * stepH, w - cut * 2 - 12, stepH + 0.5).fill({
				color: 0xbfa8ff,
				alpha: 0.075 * (1 - s / STEPS),
			});
		}
		// inner lip shade — seats the facet border on the glass
		g.poly(octagon(w - 12, h - 12, Math.max(4, cut - 7))).stroke({
			width: 10,
			color: 0x08040f,
			alpha: 0.32,
		});
		// engraved facet border: dark undercut + lavender light core (the board grooves)
		g.poly(pts).stroke({ width: 3.5, color: 0x0a0516, alpha: 0.7 });
		g.poly(pts).stroke({ width: 1.4, color: 0xd9ccff, alpha: 0.55 });
	}}
/>

<!-- light pass: accent breathe + traveling shimmer + facet gems (additive) -->
<Graphics
	blendMode="add"
	draw={(g) => {
		const t = trailClock.t;
		const w = props.width;
		const h = props.height;
		const pts = octagon(w, h, cut);
		const breathe = 0.75 + 0.25 * Math.sin(t * Math.PI * 1.4);
		const col = props.accent ?? paletteAt(t * 0.18);

		// soft accent halo hugging the facet line
		g.poly(pts).stroke({ width: 10, color: col, alpha: 0.1 * breathe });
		g.poly(pts).stroke({ width: 3, color: col, alpha: 0.4 * breathe });

		// traveling shimmer: one luminous run of the perimeter, prism light on the facet
		const total = perimeterLength(pts);
		const runLen = total * 0.16;
		const head = ((t * 0.14) % 1) * total;
		const SAMPLES = 14;
		for (let pass = 0; pass < 2; pass++) {
			for (let i = 0; i <= SAMPLES; i++) {
				const p = perimeterPoint(pts, (head + (i / SAMPLES) * runLen) % total);
				if (i === 0) g.moveTo(p.x, p.y);
				else g.lineTo(p.x, p.y);
			}
			g.stroke(
				pass === 0
					? { width: 5, color: col, alpha: 0.45 * breathe, cap: 'round', join: 'round' }
					: { width: 1.6, color: 0xffffff, alpha: 0.6 * breathe, cap: 'round', join: 'round' },
			);
		}

		// facet gems: tiny diamonds at the cut vertices, twinkling out of phase
		const n = pts.length / 2;
		for (let k = 0; k < n; k++) {
			const gx = pts[k * 2];
			const gy = pts[k * 2 + 1];
			const tw = (Math.sin(t * Math.PI * 2.6 + k * 1.9) + 1) / 2;
			const r = 2 + 2.6 * tw;
			g.poly([gx, gy - r, gx + r, gy, gx, gy + r, gx - r, gy]).fill({
				color: 0xffffff,
				alpha: 0.25 + 0.5 * tw,
			});
		}
	}}
/>
{@render props.children?.()}
