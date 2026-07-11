<script lang="ts">
	import { Rectangle, Sprite } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import BackgroundParticles from './BackgroundParticles.svelte';

	const context = getContext();
	const showBaseBackground = $derived(context.stateGame.gameType === 'basegame');
	const showFeatureBackground = $derived(context.stateGame.gameType === 'freegame');

	// COVER-crop (never stretch): scale so the image covers the canvas, centre-anchored.
	// Both backgrounds (light sky-islands = base, aurora night = feature) are 2048x1143.
	const BG = { width: 2048, height: 1143 };
	const cover = $derived.by(() => {
		const c = context.stateLayoutDerived.canvasSizes();
		const s = Math.max(c.width / BG.width, c.height / BG.height);
		return {
			anchor: 0.5,
			x: c.width * 0.5,
			y: c.height * 0.5,
			width: BG.width * s,
			height: BG.height * s,
		};
	});
</script>

<Rectangle {...context.stateLayoutDerived.canvasSizes()} backgroundColor={0x05030a} zIndex={-3} />

<!-- fast crossfade: the day<->night swap happens UNDER the transition curtain, so it must
     complete before the reveal -->
<FadeContainer show={showBaseBackground} duration={300} zIndex={-2}>
	<Sprite key="bgBase" {...cover} />
</FadeContainer>

<FadeContainer show={showFeatureBackground} duration={300} zIndex={-1}>
	<Sprite key="bgFeature" {...cover} />
</FadeContainer>

<!-- living ambient motes over the clean plates (the baked particles, animated) -->
<BackgroundParticles />
