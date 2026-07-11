<script lang="ts">
	// Loading screen — Prism Path logo + code-drawn prism progress bar (no template loader
	// spine / progress sprites). Press to continue, then the prism curtain into the game.
	import { Container, Sprite, Graphics } from 'pixi-svelte';
	import { FadeContainer, LoadingProgress } from 'components-pixi';
	import { MainContainer } from 'components-layout';
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';
	import { paletteAt } from '../game/motion';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import TransitionAnimation from './TransitionAnimation.svelte';
	import PressToContinue from './PressToContinue.svelte';

	type Props = {
		onloaded: () => void;
	};

	const props: Props = $props();
	const context = getContext();

	let loadingType = $state<'start' | 'transition'>('start');

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});

	// generated logo is 760x716
	const LOGO_W = 430;
	const LOGO_H = LOGO_W * (716 / 760);
	const BAR_W = 430;
	const BAR_H = 26;
</script>

<!-- logo and loading progress -->
<FadeContainer show={loadingType === 'start'}>
	<MainContainer>
		<Container
			x={context.stateLayoutDerived.mainLayout().width * 0.5}
			y={context.stateLayoutDerived.mainLayout().height * 0.5}
		>
			<!-- soft glow halo behind the logo -->
			<Graphics
				blendMode="add"
				draw={(g) => {
					const t = trailClock.t;
					const breathe = 0.75 + 0.25 * Math.sin(t * Math.PI * 1.1);
					g.circle(0, -40, 265 * breathe).fill({ color: paletteAt(t * 0.12), alpha: 0.07 });
					g.circle(0, -40, 170 * breathe).fill({ color: 0xffffff, alpha: 0.05 });
				}}
			/>
			<Sprite key="logo" anchor={0.5} y={-40} width={LOGO_W} height={LOGO_H} />

			{#if !context.stateApp.loaded}
				<LoadingProgress y={225} width={BAR_W} height={BAR_H}>
					{#snippet background(sizes)}
						<Graphics
							draw={(g) => {
								g.roundRect(0, 0, sizes.width, sizes.height, sizes.height / 2).fill({ color: 0x120d1c, alpha: 0.95 });
							}}
						/>
					{/snippet}
					{#snippet progress(sizes)}
						<Graphics
							draw={(g) => {
								const t = trailClock.t;
								const N = 18;
								for (let i = 0; i < N; i++) {
									const x0 = (sizes.width * i) / N;
									g.rect(x0, 2, sizes.width / N + 1, sizes.height - 4).fill({
										color: paletteAt(i / N - t * 0.35),
										alpha: 0.95,
									});
								}
								g.rect(0, sizes.height * 0.18, sizes.width, sizes.height * 0.2).fill({ color: 0xffffff, alpha: 0.35 });
							}}
						/>
					{/snippet}
					{#snippet frame(sizes)}
						<Graphics
							draw={(g) => {
								const t = trailClock.t;
								g.roundRect(0, 0, sizes.width, sizes.height, sizes.height / 2).stroke({
									width: 2.5,
									color: paletteAt(t * 0.22),
									alpha: 0.9,
								});
								g.roundRect(2, 2, sizes.width - 4, sizes.height - 4, (sizes.height - 4) / 2).stroke({
									width: 1,
									color: 0xffffff,
									alpha: 0.3,
								});
							}}
						/>
					{/snippet}
				</LoadingProgress>
			{/if}
		</Container>
	</MainContainer>
</FadeContainer>

<!-- press to continue -->
<FadeContainer show={loadingType === 'start' && context.stateApp.loaded}>
	<PressToContinue onpress={() => (loadingType = 'transition')} />
</FadeContainer>

<!-- transition between the loading screen and the game -->
<FadeContainer show={loadingType === 'transition'}>
	<TransitionAnimation oncomplete={props.onloaded} />
</FadeContainer>
