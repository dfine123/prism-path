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
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { BitmapText, Container, Graphics } from 'pixi-svelte';
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, paletteAt } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	const PANEL_W = SYMBOL_SIZE * 4.8;
	const PANEL_H = SYMBOL_SIZE * 3.2;

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
			<!-- soft rays behind the panel -->
			<Graphics
				blendMode="add"
				draw={(g) => {
					for (let i = 0; i < 10; i++) {
						const a0 = secs * 0.14 + (i / 10) * Math.PI * 2;
						const w = ((Math.PI * 2) / 10) * 0.36;
						g.moveTo(0, 0)
							.arc(0, 0, SYMBOL_SIZE * 4.6, a0 - w / 2, a0 + w / 2)
							.lineTo(0, 0)
							.fill({ color: paletteAt(i / 10 + secs * 0.1), alpha: 0.06 });
					}
				}}
			/>
			<PrismPanel width={PANEL_W} height={PANEL_H}>
				<BitmapText
					anchor={0.5}
					y={-PANEL_H * 0.28}
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
