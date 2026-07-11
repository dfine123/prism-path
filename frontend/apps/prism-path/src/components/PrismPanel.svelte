<script lang="ts">
	// Shared dark-crystal UI panel: deep plate + animated prism border + soft glow. Centered
	// on its origin — callers position the centre. Used by FS intro/counter/outro panels.
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { paletteAt } from '../game/motion';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	type Props = {
		width: number;
		height: number;
		radius?: number;
		children?: Snippet;
	};
	const props: Props = $props();
	const radius = $derived(props.radius ?? 20);

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});
</script>

<!-- plate (normal blend: real surface, not light) -->
<Graphics
	draw={(g) => {
		const w = props.width;
		const h = props.height;
		g.roundRect(-w / 2, -h / 2, w, h, radius).fill({ color: 0x120d1c, alpha: 0.94 });
		g.roundRect(-w / 2, -h / 2, w, h, radius).stroke({ width: 3, color: 0x0b0814, alpha: 1 });
	}}
/>
<!-- animated prism border + glow (additive light) -->
<Graphics
	blendMode="add"
	draw={(g) => {
		const t = trailClock.t;
		const w = props.width;
		const h = props.height;
		const breathe = 0.75 + 0.25 * Math.sin(t * Math.PI * 1.4);
		const col = paletteAt(t * 0.22);
		g.roundRect(-w / 2, -h / 2, w, h, radius).stroke({ width: 10, color: col, alpha: 0.14 * breathe });
		g.roundRect(-w / 2, -h / 2, w, h, radius).stroke({ width: 3.5, color: col, alpha: 0.8 * breathe });
		g.roundRect(-w / 2 + 4, -h / 2 + 4, w - 8, h - 8, Math.max(6, radius - 5)).stroke({
			width: 1.2,
			color: 0xffffff,
			alpha: 0.35 * breathe,
		});
	}}
/>
{@render props.children?.()}
