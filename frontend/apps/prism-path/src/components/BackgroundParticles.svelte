<script lang="ts">
	// Ambient background particles — the LIVING version of the motes baked into the original
	// background art (the plates are now clean). Rendered with real bokeh textures (gaussian
	// orb + occasional 4-point star glint), NOT flat circles: soft varied glows that rise,
	// sway and twinkle. Warm gold/white in the day realm; denser gold + cool blue at night.
	import { onMount } from 'svelte';
	import { Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	const context = getContext();

	type Mote = {
		fx: number;
		fy: number;
		size: number; // display px at twinkle mid
		rise: number;
		sway: number;
		twSpd: number;
		phase: number;
		hue: number;
		star: boolean; // gets a rotating 4-point glint on top
		bokeh: boolean; // big soft out-of-focus orb (low alpha)
	};

	const MOTES: Mote[] = Array.from({ length: 46 }, (_, i) => {
		const bokeh = i % 9 === 0; // a few big dreamy orbs
		return {
			fx: Math.random(),
			fy: Math.random(),
			size: bokeh ? 34 + Math.random() * 30 : 7 + Math.random() * 14,
			rise: (bokeh ? 0.003 : 0.005) + Math.random() * 0.011,
			sway: 0.12 + Math.random() * 0.4,
			twSpd: 0.3 + Math.random() * 0.65,
			phase: Math.random() * Math.PI * 2,
			hue: Math.random(),
			star: !bokeh && i % 5 === 0, // ~20% of small motes glint
			bokeh,
		};
	});

	const DAY = [0xffe9b0, 0xfff6da, 0xffffff];
	const NIGHT = [0xffd88a, 0x9fd8ff, 0xffffff];

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});

	const rendered = $derived.by(() => {
		const t = trailClock.t;
		const c = context.stateLayoutDerived.canvasSizes();
		const feature = context.stateGame.gameType === 'freegame';
		const palette = feature ? NIGHT : DAY;
		const count = feature ? MOTES.length : 34;
		const modeMul = feature ? 1.1 : 0.85;
		return MOTES.slice(0, count).map((m) => {
			const y = ((((m.fy - t * m.rise) % 1) + 1) % 1) * c.height;
			const x = (m.fx + Math.sin(t * m.sway + m.phase) * 0.012) * c.width;
			const tw = 0.5 + 0.5 * Math.sin(t * m.twSpd * Math.PI * 2 + m.phase);
			const tint = palette[Math.floor(m.hue * palette.length) % palette.length];
			const size = m.size * (0.8 + 0.4 * tw);
			// dialed WAY down (operator: flashing too bright) — a shine you notice only
			// when you look for it, never a flash that pulls the eye from the reels
			const alpha = (m.bokeh ? 0.05 + 0.07 * tw : 0.09 + 0.16 * tw) * modeMul;
			return {
				x,
				y,
				size,
				alpha,
				tint,
				star: m.star,
				starRot: t * 0.12 + m.phase,
				starSize: size * 2.4,
				// star cross only crests near the twinkle peak, and gently (was 1.6x — a strobe)
				starAlpha: Math.max(0, tw - 0.72) * 0.7 * modeMul,
			};
		});
	});
</script>

{#each rendered as p, i (i)}
	<Sprite
		key="mote"
		anchor={0.5}
		x={p.x}
		y={p.y}
		width={p.size}
		height={p.size}
		alpha={p.alpha}
		tint={p.tint}
		blendMode="add"
		zIndex={-1}
	/>
	{#if p.star && p.starAlpha > 0.02}
		<Sprite
			key="moteStar"
			anchor={0.5}
			x={p.x}
			y={p.y}
			rotation={p.starRot}
			width={p.starSize}
			height={p.starSize}
			alpha={p.starAlpha}
			tint={p.tint}
			blendMode="add"
			zIndex={-1}
		/>
	{/if}
{/each}
