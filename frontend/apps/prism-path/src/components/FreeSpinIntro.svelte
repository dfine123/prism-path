<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
	// FREE SPINS intro ON THE WIN-BOX PLAQUE — the game's one approved dialog
	// family (opaque violet plaque, accent light, corner gems, crest). Normal
	// trigger rides a cyan level-7 plaque; a SUPER buy gets the gold level-9 trim
	// (side stones + crown + gold gem rain). The count lands with an impact pop
	// and a glint burst; sub-line in the label voice; invite seated under.
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { BitmapText, Container, Sprite } from 'pixi-svelte';
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor } from '../game/motion';
	import WinBox from './WinBox.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	const GOLD = 0xffd25e;
	const CYAN = 0x2bb8e8;
	const BOX_H = SYMBOL_SIZE * 3.6;

	// SUPER buys get their own identity: gold ceremony trim, 'a dragon every spin'
	const isSuper = $derived(stateBet.activeBetModeKey === 'SUPER');
	const accent = $derived(isSuper ? GOLD : CYAN);

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
				// AUTOPLAY / SPACE-HOLD auto-advance after a readable hold (a held key
				// can never produce the fresh keydown PressToContinue needs).
				if (stateBetDerived.hasAutoBetCounter() || stateBet.isSpaceHold) {
					waitForTimeout(1600).then(() => {
						if (oncomplete === resolve) oncomplete();
					});
				}
			});
		},
	});

	const secs = $derived(t / 1000);
	const landAge = $derived((t - popStart) / 1000);
	// count: impact pop keyed to popStart (re-pops on a retrigger update), settles
	// to EXACTLY 1 so it breathes WITH the plaque
	const numScale = $derived.by(() => {
		const u = clamp01(landAge / 0.46);
		return u < 1 ? 2.1 - 1.1 * EASE.impact(u) : 1;
	});
	const subIn = $derived(clamp01((landAge - 0.3) / 0.35));
	// glint burst as the count lands
	const burstU = $derived(clamp01((landAge - 0.08) / 0.55));
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x05030a} backgroundAlpha={0.62} />

	<MainContainer>
		<Container
			x={context.stateGameDerived.boardLayout().x}
			y={context.stateGameDerived.boardLayout().y}
		>
			<!-- THE plaque: win-box family; SUPER rides the crowned gold trim -->
			<WinBox
				level={isSuper ? 9 : 7}
				accentOverride={accent}
				fixedText={isSuper ? 'SUPER FREE SPINS' : 'FREE SPINS'}
			>
				<!-- the count: the big beat (children anchor sits in the lower chamber) -->
				<Container y={-SYMBOL_SIZE * 0.16} scale={numScale}>
					<BitmapText
						anchor={0.5}
						text={`${freeSpinsFromEvent}`}
						style={prismStyle(SYMBOL_SIZE * 1.15)}
					/>
				</Container>
				{#if burstU > 0 && burstU < 1}
					{#each Array.from({ length: 6 }, (_, i) => i) as i (i)}
						{@const a = (i / 6) * Math.PI * 2 + 0.4}
						{@const r = SYMBOL_SIZE * (0.4 + 1.5 * EASE.settle(burstU))}
						<Sprite
							key="moteStar"
							anchor={0.5}
							blendMode="add"
							tint={lerpColor(accent, 0xffffff, 0.6)}
							x={Math.cos(a) * r * 1.25}
							y={-SYMBOL_SIZE * 0.16 + Math.sin(a) * r * 0.8}
							width={SYMBOL_SIZE * 0.32 * (1 - burstU * 0.6)}
							height={SYMBOL_SIZE * 0.32 * (1 - burstU * 0.6)}
							rotation={a + burstU * 1.2}
							alpha={0.85 * (1 - burstU)}
						/>
					{/each}
				{/if}
				<!-- sub-line in the LABEL voice -->
				<Container y={SYMBOL_SIZE * 0.66} alpha={subIn}>
					<BitmapText
						anchor={0.5}
						text={isSuper ? 'A DRAGON EVERY SPIN' : 'THE DRAGONS AWAKEN'}
						style={superLabelStyle(SYMBOL_SIZE * 0.2, { align: 'center' })}
					/>
				</Container>
			</WinBox>

			<!-- the invite, seated with the plaque -->
			{#if show}
				<BitmapText
					anchor={0.5}
					y={BOX_H / 2 + SYMBOL_SIZE * 0.34}
					text="PRESS ANYWHERE TO CONTINUE"
					alpha={(0.62 + 0.38 * (Math.sin(secs * Math.PI * 1.3) + 1) * 0.5) *
						clamp01((landAge - 0.7) / 0.35)}
					style={superLabelStyle(SYMBOL_SIZE * 0.185, { align: 'center' })}
				/>
			{/if}
		</Container>
	</MainContainer>

	{#if show}
		<PressToContinue showLabel={false} onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
