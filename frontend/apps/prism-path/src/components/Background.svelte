<script lang="ts">
	import { Rectangle, Sprite } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { SECOND } from 'constants-shared/time';

	import { getContext } from '../game/context';

	const context = getContext();
	const showBaseBackground = $derived(context.stateGame.gameType === 'basegame');
	const showFeatureBackground = $derived(context.stateGame.gameType === 'freegame');

	// COVER-crop (never stretch): scale so the image covers the canvas, centre-anchored.
	// Both generated backgrounds are 1376x768.
	const BG = { width: 1376, height: 768 };
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

<FadeContainer show={showBaseBackground} duration={SECOND} zIndex={-2}>
	<Sprite key="bgBase" {...cover} />
</FadeContainer>

<FadeContainer show={showFeatureBackground} duration={SECOND} zIndex={-1}>
	<Sprite key="bgFeature" {...cover} />
</FadeContainer>
