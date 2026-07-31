<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
	// FREE SPINS intro — code-drawn prism panel (no template spine): dim veil, crystal panel,
	// FREE SPINS wordmark, spin count dropping in with an impact pop, press to continue.
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { FadeContainer, ResponsiveBitmapText } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { BitmapText, Container, Graphics, FillGradient } from 'pixi-svelte';
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01 } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	// the panel is sized to the WORDMARK, and the wordmark auto-fits inside it — the fixed
	// pairing before this let "FREE SPINS" run straight out past both edges of the plaque
	const PANEL_W = SYMBOL_SIZE * 5.9;
	const PANEL_H = SYMBOL_SIZE * 3.3;
	const WORD_MAX_W = PANEL_W - SYMBOL_SIZE * 1.0;

	let show = $state(false);
	let freeSpinsFromEvent = $state(0);
	let oncomplete = $state(() => {});
	let popStart = $state(0);
	let t = $state(0);

	onMount(() => {
		let raf = 0;
		const frame = () => {
			t = performance.now();
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	context.eventEmitter.subscribeOnMount({
		freeSpinIntroShow: () => {
			show = true;
			popStart = performance.now();
		},
		freeSpinIntroHide: () => (show = false),
		freeSpinIntroUpdate: async (emitterEvent) => {
			freeSpinsFromEvent = emitterEvent.totalFreeSpins;
			popStart = performance.now();
			await waitForResolve((resolve) => {
				oncomplete = resolve;
				// AUTOPLAY / SPACE-HOLD can never produce the fresh keydown PressToContinue
				// needs (auto-repeat is filtered) — auto-advance after a readable hold.
				// Generation-guarded so a stale timer can't resolve a later intro's await.
				if (stateBetDerived.hasAutoBetCounter() || stateBet.isSpaceHold) {
					waitForTimeout(1600).then(() => {
						if (oncomplete === resolve) oncomplete();
					});
				}
			});
		},
	});

	// number impact pop (anticipation handled by the transition that precedes this screen)
	const numScale = $derived.by(() => {
		const u = clamp01((t - popStart) / 460);
		if (u < 1) return 2.1 - 1.1 * EASE.impact(u);
		return 1 + 0.025 * Math.sin((t / 1000) * Math.PI * 1.5);
	});
	const secs = $derived(t / 1000);
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x05030a} backgroundAlpha={0.62} />

	<MainContainer>
		<Container
			x={context.stateGameDerived.boardLayout().x}
			y={context.stateGameDerived.boardLayout().y}
		>
			<!-- NATURAL BLOOM behind the panel: one soft radial falloff that breathes, in a
			     single cool light. The rainbow wedge-fan it replaces was a hard-edged
			     starburst of five hues — the tell-tale "cheap" look. -->
			<Graphics
				blendMode="add"
				draw={(g) => {
					const breathe = 0.86 + 0.14 * Math.sin(secs * Math.PI * 0.8);
					const R = SYMBOL_SIZE * 4.9 * breathe;
					g.circle(0, 0, R).fill(
						new FillGradient({
							type: 'radial',
							center: { x: 0.5, y: 0.5 },
							innerRadius: 0,
							outerCenter: { x: 0.5, y: 0.5 },
							outerRadius: 0.5,
							textureSpace: 'local',
							colorStops: [
								{ offset: 0, color: 'rgba(190,225,255,0.30)' },
								{ offset: 0.42, color: 'rgba(150,120,255,0.13)' },
								{ offset: 1, color: 'rgba(120,90,220,0)' },
							],
						}),
					);
				}}
			/>
			<PrismPanel width={PANEL_W} height={PANEL_H}>
				<ResponsiveBitmapText
					anchor={0.5}
					y={-PANEL_H * 0.28}
					maxWidth={WORD_MAX_W}
					text="FREE SPINS"
					style={prismStyle(SYMBOL_SIZE * 0.72, { align: 'center' })}
				/>
				<Container y={PANEL_H * 0.08} scale={numScale}>
					<BitmapText anchor={0.5} text={`${freeSpinsFromEvent}`} style={prismStyle(SYMBOL_SIZE * 1.5)} />
				</Container>
				<!-- sub-line in the LABEL voice (Fredoka letterspaced caps) — Chango blobbed at
				     this size and made the whole panel read heavy -->
				<BitmapText
					anchor={0.5}
					y={PANEL_H * 0.37}
					text="THE DRAGONS AWAKEN"
					style={superLabelStyle(SYMBOL_SIZE * 0.22, { align: 'center' })}
				/>
			</PrismPanel>
		</Container>
	</MainContainer>

	<!-- unmount the full-screen catcher the instant hiding starts — an invisible fading
	     rect must not swallow board presses -->
	{#if show}
		<PressToContinue onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
