<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
	// FREE SPINS intro — LIMESTONE PLAQUE ceremony (operator: ornate art read as
	// overdone; the ceremony plate is the board frame's own hand-drawn material, like
	// the counter). Code stages it: impact entrance with a silhouette shockwave,
	// staggered text reveals, a glint burst as the count lands. Mode identity (SUPER)
	// is carried entirely by the accent light — the stone never changes.
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { FadeContainer, ResponsiveBitmapText } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { BitmapText, Container, Graphics, Sprite } from 'pixi-svelte';
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor } from '../game/motion';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	// plate geometry: art is 1320x742, glass window inset 0.129H per side — text rows
	// seat symmetrically inside ±0.33H usable interior
	const PLATE_W = SYMBOL_SIZE * 7.15;
	const PLATE_H = PLATE_W * (742 / 1320);
	const GOLD = 0xffd25e;
	const CYAN = 0x2bb8e8;

	// SUPER buys get their own identity in LIGHT: gold accent, named, 'a dragon every spin'
	const isSuper = $derived(stateBet.activeBetModeKey === 'SUPER');
	const accent = $derived(isSuper ? GOLD : CYAN);

	// silhouette for the landing shockwave: the plate's chamfered rectangle
	const CUT = PLATE_H * 0.148;
	const octagon = (w: number, h: number): number[] => {
		const w2 = w / 2;
		const h2 = h / 2;
		const c = CUT;
		return [-w2 + c, -h2, w2 - c, -h2, w2, -h2 + c, w2, h2 - c, w2 - c, h2, -w2 + c, h2, -w2, h2 - c, -w2, -h2 + c];
	};
	const scaleOct = (pts: number[], sc: number) => pts.map((v) => v * sc);

	let show = $state(false);
	let freeSpinsFromEvent = $state(0);
	let oncomplete = $state(() => {});
	let shownAtMs = 0;
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
			shownAtMs = performance.now();
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

	const secs = $derived(t / 1000);
	const age = $derived(show ? (t - shownAtMs) / 1000 : 0);

	// ---- ceremony beats ----
	// plate: impact entrance, then a barely-there breath
	const plateIn = $derived(clamp01(age / 0.42));
	const plateScale = $derived.by(() => {
		if (plateIn < 1) return 1.22 - 0.22 * EASE.impact(plateIn);
		return 1 + 0.005 * Math.sin(secs * Math.PI * 0.9);
	});
	const plateAlpha = $derived(clamp01(age / 0.15));

	// wordmark drops in just behind the plate's landing
	const wAge = $derived(clamp01((age - 0.14) / 0.34));
	// sub-line eases in last
	const sAge = $derived(clamp01((age - 0.52) / 0.4));

	// count: impact pop keyed to popStart (re-pops on a retrigger update). After the
	// impact it settles to EXACTLY 1 and inherits the plate container's breath — its
	// own idle sine at a different frequency read as the count and box ALTERNATING
	const nAge = $derived((t - popStart) / 1000);
	const numScale = $derived.by(() => {
		const u = clamp01(nAge / 0.46);
		return u < 1 ? 2.1 - 1.1 * EASE.impact(u) : 1;
	});
	// glint burst as the count lands: 6 star sparks thrown radially from the number
	const burstU = $derived(clamp01((nAge - 0.08) / 0.55));
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x05030a} backgroundAlpha={0.62} />

	<MainContainer>
		<Container
			x={context.stateGameDerived.boardLayout().x}
			y={context.stateGameDerived.boardLayout().y}
		>
			<!-- soft backdrop bloom (textured gaussian, breathes slowly) -->
			<Sprite
				key="mote"
				anchor={0.5}
				blendMode="add"
				tint={lerpColor(accent, 0xffffff, 0.3)}
				width={SYMBOL_SIZE * 9.6 * (0.92 + 0.08 * Math.sin(secs * Math.PI * 0.8))}
				height={SYMBOL_SIZE * 7 * (0.92 + 0.08 * Math.sin(secs * Math.PI * 0.8))}
				alpha={0.22 * plateAlpha}
			/>

			<!-- slow gem rain BEHIND the plate: depth between the veil and the plaque -->
			{#each Array.from({ length: 9 }, (_, i) => i) as i (i)}
				{@const u = ((secs * (0.06 + 0.025 * ((i * 7) % 3)) + i * 0.23) % 1)}
				<Sprite
					key="moteStar"
					anchor={0.5}
					blendMode="add"
					tint={lerpColor(accent, 0xffffff, 0.5)}
					x={(((i * 0.618) % 1) - 0.5) * PLATE_W * 1.5}
					y={(u - 0.5) * PLATE_H * 1.9}
					width={SYMBOL_SIZE * (0.14 + 0.08 * ((i * 5) % 3))}
					height={SYMBOL_SIZE * (0.14 + 0.08 * ((i * 5) % 3))}
					rotation={u * Math.PI * 0.6 + i}
					alpha={0.22 * Math.sin(u * Math.PI) * plateAlpha}
				/>
			{/each}

			<Container scale={plateScale} alpha={plateAlpha}>
				<!-- THE PLATE: limestone plaque in the board frame's hand-drawn ink -->
				<Sprite key="plateStone" anchor={0.5} width={PLATE_W} height={PLATE_H} />

				<!-- pool of light under the count -->
				<Sprite
					key="mote"
					anchor={0.5}
					blendMode="add"
					tint={lerpColor(accent, 0xffffff, 0.3)}
					y={PLATE_H * 0.055}
					width={SYMBOL_SIZE * 3.2}
					height={SYMBOL_SIZE * 2.3}
					alpha={0.3 + 0.25 * (1 - burstU) + 0.05 * Math.sin(secs * Math.PI * 1.1)}
				/>

				<!-- wordmark: drops from above with the impact settle. ROW RHYTHM: the stone
				     window is symmetric (usable ±0.33H) — word -0.19 / count +0.055 /
				     sub +0.28 -->
				<Container
					y={-PLATE_H * 0.19 - SYMBOL_SIZE * 0.3 * (1 - EASE.settle(wAge))}
					alpha={clamp01(wAge * 2.2)}
					scale={1.25 - 0.25 * EASE.impact(wAge)}
				>
					<ResponsiveBitmapText
						anchor={0.5}
						maxWidth={PLATE_W * 0.62}
						text={isSuper ? 'SUPER FREE SPINS' : 'FREE SPINS'}
						style={prismStyle(SYMBOL_SIZE * 0.58, { align: 'center' })}
					/>
				</Container>

				<!-- the count: the big beat -->
				<Container y={PLATE_H * 0.055} scale={numScale}>
					<BitmapText anchor={0.5} text={`${freeSpinsFromEvent}`} style={prismStyle(SYMBOL_SIZE * 1.2)} />
				</Container>

				<!-- glint burst thrown from the count as it lands -->
				{#if burstU > 0 && burstU < 1}
					{#each Array.from({ length: 6 }, (_, i) => i) as i (i)}
						{@const a = (i / 6) * Math.PI * 2 + 0.4}
						{@const r = SYMBOL_SIZE * (0.5 + 1.7 * EASE.settle(burstU))}
						<Sprite
							key="moteStar"
							anchor={0.5}
							blendMode="add"
							tint={lerpColor(accent, 0xffffff, 0.6)}
							x={Math.cos(a) * r * 1.25}
							y={PLATE_H * 0.055 + Math.sin(a) * r * 0.85}
							width={SYMBOL_SIZE * 0.34 * (1 - burstU * 0.6)}
							height={SYMBOL_SIZE * 0.34 * (1 - burstU * 0.6)}
							rotation={a + burstU * 1.2}
							alpha={0.85 * (1 - burstU)}
						/>
					{/each}
				{/if}

				<!-- sub-line in the LABEL voice -->
				<Container y={PLATE_H * 0.28 + SYMBOL_SIZE * 0.12 * (1 - EASE.settle(sAge))} alpha={sAge}>
					<BitmapText
						anchor={0.5}
						text={isSuper ? 'A DRAGON EVERY SPIN' : 'THE DRAGONS AWAKEN'}
						style={superLabelStyle(SYMBOL_SIZE * 0.2, { align: 'center' })}
					/>
				</Container>

				<!-- the invite, seated with the plaque (not lost at the screen edge) -->
				<BitmapText
					anchor={0.5}
					y={PLATE_H / 2 + SYMBOL_SIZE * 0.32}
					text="PRESS ANYWHERE TO CONTINUE"
					alpha={(0.62 + 0.38 * (Math.sin(secs * Math.PI * 1.3) + 1) * 0.5) *
						clamp01((age - 0.7) / 0.35)}
					style={superLabelStyle(SYMBOL_SIZE * 0.185, { align: 'center' })}
				/>

			</Container>

			<!-- landing shockwave: the plate's silhouette bursting outward, twin rings -->
			{#if age > 0 && age < 0.62}
				<Graphics
					blendMode="add"
					draw={(g) => {
						const base = octagon(PLATE_W, PLATE_H);
						const s1 = clamp01(age / 0.5);
						g.poly(scaleOct(base, 1 + 0.85 * EASE.settle(s1))).stroke({
							width: 3 + 10 * (1 - s1),
							color: lerpColor(0xffffff, accent, s1),
							alpha: 0.5 * (1 - s1),
							join: 'miter',
						});
						const s2 = clamp01((age - 0.09) / 0.5);
						if (s2 > 0) {
							g.poly(scaleOct(base, 1 + 0.5 * EASE.settle(s2))).stroke({
								width: 2 + 6 * (1 - s2),
								color: accent,
								alpha: 0.35 * (1 - s2),
								join: 'miter',
							});
						}
					}}
				/>
			{/if}
		</Container>
	</MainContainer>

	<!-- unmount the full-screen catcher the instant hiding starts — an invisible fading
	     rect must not swallow board presses -->
	{#if show}
		<PressToContinue showLabel={false} onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
