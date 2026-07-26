<script lang="ts">
	import { Graphics } from 'pixi-svelte';

	import { SUPER_UI, prismAt } from '../theme';

	// The Crystal Console surface primitive — "cut crystal" construction, layered:
	//   grounding outline -> glass fill -> gradient bands -> bevel -> rim -> edge-light
	// Tones: 'panel' (deck plates, pods; optional prism SEAM along the top edge),
	//        'control' (keys — domed: bottom shade + top gloss crescents),
	//        'hero' (lighter key core), 'inset' (recessed instrument well).
	type Props = {
		x?: number;
		y?: number;
		width: number;
		height: number;
		radius?: number;
		tone?: 'panel' | 'control' | 'hero' | 'inset';
		lit?: boolean; // hovered rim-light
		accent?: number | null; // active ring colour (gold toggle, win accent)
		seam?: boolean; // prism gradient light-line along the top edge (deck signature)
		alpha?: number;
	};

	const props: Props = $props();
	const T = SUPER_UI;

	const tone = $derived(props.tone ?? 'control');
	const r = $derived(Math.min(props.radius ?? T.railR, props.height / 2, props.width / 2));
	const isRound = $derived(r >= Math.min(props.width, props.height) / 2 - 1.5);
</script>

<Graphics
	x={props.x ?? 0}
	y={props.y ?? 0}
	alpha={props.alpha ?? 1}
	draw={(g) => {
		const w = props.width;
		const h = props.height;

		if (tone === 'inset') {
			// recessed well: darker glass, inverted bevel (shadow lip top, light lip bottom)
			g.roundRect(-w / 2, -h / 2, w, h, r).fill({ color: 0x0c0716, alpha: 0.62 });
			g.roundRect(-w / 2, -h / 2, w, h, r).stroke({ width: 1.5, color: 0x080510, alpha: 0.9 });
			g.rect(-w / 2 + r * 0.7, -h / 2 + 1.5, w - r * 1.4, h * 0.22).fill({ color: 0x000000, alpha: 0.22 });
			g.moveTo(-w / 2 + r, h / 2 - 1.5)
				.lineTo(w / 2 - r, h / 2 - 1.5)
				.stroke({ width: 1.5, color: 0xffffff, alpha: 0.09, cap: 'round' });
			if (props.accent != null) {
				g.roundRect(-w / 2 - 1.5, -h / 2 - 1.5, w + 3, h + 3, r + 1.5).stroke({
					width: 2.5,
					color: props.accent,
					alpha: 0.9,
				});
			}
			return;
		}

		const fill = tone === 'hero' || props.lit ? T.color.glassHi : T.color.glass;

		// grounding outline (under everything, slightly outside)
		g.roundRect(-w / 2 - 2, -h / 2 - 2, w + 4, h + 4, r + 2).stroke({
			width: tone === 'panel' ? 4 : 2.5,
			color: 0x080510,
			alpha: 0.88,
		});
		// glass plate
		g.roundRect(-w / 2, -h / 2, w, h, r).fill({ color: fill, alpha: T.glassAlpha });

		if (isRound && tone !== 'panel') {
			// DOMED KEY: bottom shade crescent + top gloss crescent
			// (explicit moveTo before each arc — no stray path-connector lines)
			const cr = Math.min(w, h) / 2;
			g.moveTo(Math.cos(Math.PI * 0.15) * cr * 0.8, Math.sin(Math.PI * 0.15) * cr * 0.8);
			g.arc(0, 0, cr * 0.8, Math.PI * 0.15, Math.PI * 0.85).stroke({
				width: cr * 0.26,
				color: 0x000000,
				alpha: 0.16,
				cap: 'round',
			});
			g.moveTo(Math.cos(Math.PI * 1.15) * cr * 0.78, Math.sin(Math.PI * 1.15) * cr * 0.78);
			g.arc(0, 0, cr * 0.78, Math.PI * 1.15, Math.PI * 1.85).stroke({
				width: cr * 0.17,
				color: 0xffffff,
				alpha: 0.09,
				cap: 'round',
			});
		} else {
			// PLATE: light-top / shaded-bottom gradient bands (inset past the end caps)
			g.rect(-w / 2 + r * 0.8, -h / 2 + 3, w - r * 1.6, h * 0.32).fill({ color: 0xffffff, alpha: 0.045 });
			g.rect(-w / 2 + r * 0.8, h / 2 - h * 0.26, w - r * 1.6, h * 0.26 - 3).fill({ color: 0x000000, alpha: 0.2 });
		}

		// rim
		g.roundRect(-w / 2, -h / 2, w, h, r).stroke({
			width: props.lit ? 3 : 1.5,
			color: props.lit ? T.color.edgeLit : T.color.edge,
			alpha: props.lit ? 0.95 : 0.8,
		});
		// top edge-light (the "glass" read)
		g.moveTo(-w / 2 + r, -h / 2 + 1.5)
			.lineTo(w / 2 - r, -h / 2 + 1.5)
			.stroke({
				width: 2,
				color: props.lit ? T.color.edgeLit : 0xffffff,
				alpha: props.lit ? 0.5 : 0.14,
				cap: 'round',
			});

		// PRISM SEAM: the deck's signature — the brand ramp as a light-line on the top edge
		if (props.seam) {
			const segs = 36;
			const x0 = -w / 2 + r * 0.9;
			const x1 = w / 2 - r * 0.9;
			for (let i = 0; i < segs; i++) {
				const a = x0 + ((x1 - x0) * i) / segs;
				const b = x0 + ((x1 - x0) * (i + 1.06)) / segs;
				const col = prismAt(i / segs);
				g.moveTo(a, -h / 2 - 1).lineTo(b, -h / 2 - 1).stroke({ width: 6, color: col, alpha: 0.14, cap: 'butt' });
				g.moveTo(a, -h / 2 - 1).lineTo(b, -h / 2 - 1).stroke({ width: 2.5, color: col, alpha: 0.8, cap: 'butt' });
			}
		}

		// active accent ring
		if (props.accent != null) {
			g.roundRect(-w / 2 - 3, -h / 2 - 3, w + 6, h + 6, r + 3).stroke({
				width: 3.5,
				color: props.accent,
				alpha: 0.95,
			});
		}
	}}
/>
