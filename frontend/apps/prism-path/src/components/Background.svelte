<script lang="ts">
	import { Rectangle } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import BackgroundParticles from './BackgroundParticles.svelte';
	import BackgroundScene from './BackgroundScene.svelte';

	const context = getContext();
	const showBaseBackground = $derived(context.stateGame.gameType === 'basegame');
	const showFeatureBackground = $derived(context.stateGame.gameType === 'freegame');

</script>

<Rectangle {...context.stateLayoutDerived.canvasSizes()} backgroundColor={0x05030a} zIndex={-3} />

<!-- fast crossfade: the day<->night swap happens UNDER the transition curtain, so it must
     complete before the reveal -->
<!-- layered living scene: sky plate + floating island cutouts + drifting clouds
     (BackgroundScene) — replaces the flat painting sprite per scene -->
<FadeContainer show={showBaseBackground} duration={300} zIndex={-2}>
	<BackgroundScene scene="base" />
</FadeContainer>

<FadeContainer show={showFeatureBackground} duration={300} zIndex={-1}>
	<BackgroundScene scene="feature" />
</FadeContainer>

<!-- living ambient motes over the clean plates (the baked particles, animated) -->
<BackgroundParticles />
