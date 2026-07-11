<script lang="ts">
	// Ambient background particles — the LIVING version of the motes that were baked into the
	// original background art (the plates are now clean). Soft glowing orbs that rise, sway
	// and twinkle: warm gold/white in the day realm; denser gold + cool blue under the aurora.
	import { onMount } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	const context = getContext();

	type Mote = {
		fx: number; // 0..1 field position
		fy: number;
		r: number;
		rise: number; // fraction of screen height per second
		sway: number;
		twSpd: number;
		phase: number;
		hue: number; // 0..1 -> palette pick
	};

	const MOTES: Mote[] = Array.from({ length: 52 }, () => ({
		fx: Math.random(),
		fy: Math.random(),
		r: 1.6 + Math.random() * 3.2,
		rise: 0.004 + Math.random() * 0.012,
		sway: 0.15 + Math.random() * 0.45,
		twSpd: 0.35 + Math.random() * 0.75,
		phase: Math.random() * Math.PI * 2,
		hue: Math.random(),
	}));

	const DAY = [0xfff3cf, 0xffe9a8, 0xffffff];
	const NIGHT = [0xffd88a, 0x9fd8ff, 0xffffff];

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});
</script>

<Graphics
	blendMode="add"
	zIndex={-1}
	draw={(g) => {
		const t = trailClock.t;
		const c = context.stateLayoutDerived.canvasSizes();
		const feature = context.stateGame.gameType === 'freegame';
		const palette = feature ? NIGHT : DAY;
		const count = feature ? MOTES.length : 38;
		const modeMul = feature ? 1.15 : 0.85;
		for (let i = 0; i < count; i++) {
			const m = MOTES[i];
			const y = ((((m.fy - t * m.rise) % 1) + 1) % 1) * c.height;
			const x = (m.fx + Math.sin(t * m.sway + m.phase) * 0.012) * c.width;
			const tw = 0.5 + 0.5 * Math.sin(t * m.twSpd * Math.PI * 2 + m.phase);
			const col = palette[Math.floor(m.hue * palette.length) % palette.length];
			const r = m.r * (0.75 + 0.5 * tw);
			const a = (0.08 + 0.34 * tw) * modeMul;
			g.circle(x, y, r * 2.6).fill({ color: col, alpha: a * 0.3 }); // soft halo
			g.circle(x, y, r).fill({ color: col, alpha: a });
		}
	}}
/>
