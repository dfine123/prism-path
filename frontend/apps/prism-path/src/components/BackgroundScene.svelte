<script lang="ts">
	// LAYERED LIVING BACKGROUND (POLISH-ROADMAP 2.3 — operator-directed architecture).
	// The scene is built from REAL PLATES derived from the original paintings via
	// Higgsfield: one full empty-sky base, then every island and cloud as its own
	// COMPLETE cutout (each island was redrawn whole, including the parts the original
	// canvas cropped, so floating never reveals a cut edge). Composited in the
	// painting's own 2048x1143 space and animated the way a diorama moves:
	//   - islands FLOAT: slow desynchronized bob + sway; distant/small islands move
	//     less than near/large ones (natural parallax depth)
	//   - clouds DRIFT: slow horizontal shuttle
	//   - the sky plate is still
	// All motion is sub-pixel-per-frame slow; the scene should read as alive only when
	// you rest your eyes on it, never while the reels are the focus.
	import { onMount } from 'svelte';
	import { Container, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	type Props = { scene: 'base' | 'feature' };
	const props: Props = $props();
	const context = getContext();

	// same COVER mapping the old flat background used: children live in image space
	const IMG = { w: 2048, h: 1143 };
	const cover = $derived.by(() => {
		const c = context.stateLayoutDerived.canvasSizes();
		const s = Math.max(c.width / IMG.w, c.height / IMG.h);
		return { x: c.width * 0.5, y: c.height * 0.5, scale: s };
	});

	onMount(() => {
		acquireTrailClock();
		return () => releaseTrailClock();
	});
	const t = $derived(trailClock.t);

	type Layer = {
		key: string;
		x: number; // centre, image space
		y: number;
		h: number; // drawn height (width follows the texture's aspect unless w is set)
		w?: number;
		bobAmp?: number; // px, vertical float
		bobT?: number; // s, period
		swayAmp?: number; // px, horizontal float
		swayT?: number;
		driftSpan?: number; // px, slow cloud shuttle
		driftT?: number;
		ph?: number; // phase seed so nothing moves in sync
	};

	// paint order = array order (sky first, foreground bank last)
	const LAYERS: Record<'base' | 'feature', Layer[]> = {
		base: [
			{ key: 'lyDaySky', x: 1024, y: 571.5, h: 1143, w: 2048 },
			{ key: 'lyDayCloud', x: 1080, y: 310, h: 225, driftSpan: 130, driftT: 95, bobAmp: 4, bobT: 21, ph: 0.35 },
			{ key: 'lyDayIsletTL', x: 500, y: 255, h: 430, bobAmp: 11, bobT: 13, swayAmp: 6, swayT: 19, ph: 0.1 },
			{ key: 'lyDayIslandTR', x: 1545, y: 235, h: 450, bobAmp: 11, bobT: 15, swayAmp: 6, swayT: 22, ph: 0.55 },
			{ key: 'lyDayIsletC', x: 850, y: 762, h: 150, bobAmp: 9, bobT: 11, swayAmp: 4, swayT: 16, ph: 0.8 },
			{ key: 'lyDayIslandL', x: 305, y: 545, h: 960, bobAmp: 16, bobT: 16, swayAmp: 7, swayT: 23, ph: 0.0 },
			{ key: 'lyDayIslandR', x: 1758, y: 600, h: 880, bobAmp: 16, bobT: 18, swayAmp: 7, swayT: 26, ph: 0.45 },
			{ key: 'lyDayBank', x: 1024, y: 1015, h: 520, w: 2400, driftSpan: 45, driftT: 55, ph: 0.2 },
		],
		feature: [
			{ key: 'lyNightSky', x: 1024, y: 571.5, h: 1143, w: 2048 },
			{ key: 'lyNightIsletTL', x: 512, y: 245, h: 430, bobAmp: 11, bobT: 13, swayAmp: 6, swayT: 19, ph: 0.1 },
			{ key: 'lyNightIslandTR', x: 1560, y: 250, h: 470, bobAmp: 11, bobT: 15, swayAmp: 6, swayT: 22, ph: 0.55 },
			{ key: 'lyNightIsletC', x: 845, y: 770, h: 150, bobAmp: 9, bobT: 11, swayAmp: 4, swayT: 16, ph: 0.8 },
			{ key: 'lyNightIslandL', x: 300, y: 555, h: 980, bobAmp: 16, bobT: 16, swayAmp: 7, swayT: 23, ph: 0.0 },
			{ key: 'lyNightIslandR', x: 1762, y: 610, h: 900, bobAmp: 16, bobT: 18, swayAmp: 7, swayT: 26, ph: 0.45 },
			{ key: 'lyNightCloud', x: 1000, y: 1030, h: 260, driftSpan: 90, driftT: 75, bobAmp: 4, bobT: 24, ph: 0.6 },
		],
	};

	const TAU = Math.PI * 2;
	const lx = (l: Layer) =>
		l.x +
		(l.swayAmp ? l.swayAmp * Math.sin((t * TAU) / (l.swayT ?? 17) + (l.ph ?? 0) * 7) : 0) +
		(l.driftSpan ? l.driftSpan * Math.sin((t * TAU) / (l.driftT ?? 60) + (l.ph ?? 0) * 7) : 0);
	const ly = (l: Layer) => l.y + (l.bobAmp ? l.bobAmp * Math.sin((t * TAU) / (l.bobT ?? 12) + (l.ph ?? 0) * 11) : 0);
	const lw = (l: Layer) => {
		if (l.w) return l.w;
		const tex = context.stateApp.loadedAssets?.[l.key];
		const ratio = tex && tex.height ? tex.width / tex.height : 1;
		return l.h * ratio;
	};
</script>

<Container x={cover.x} y={cover.y} scale={cover.scale} pivot={{ x: IMG.w / 2, y: IMG.h / 2 }}>
	{#each LAYERS[props.scene] as l (l.key)}
		<Sprite key={l.key} anchor={0.5} x={lx(l)} y={ly(l)} width={lw(l)} height={l.h} />
	{/each}
</Container>
