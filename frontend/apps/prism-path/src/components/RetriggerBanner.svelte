<script lang="ts" module>
	export type EmitterEventRetriggerBanner = { type: 'retriggerShow'; extraSpins: number };
</script>

<script lang="ts">
	// RETRIGGER — "+N FREE SPINS" presented as its own beat. A compact gold cut-crystal
	// plaque pops in over the board centre (impact-settle, same motion voice as the win
	// box), holds just long enough to read, and collapses out. No screen takeover: the
	// scatters have already celebrated; this names what they awarded. The handler AWAITS
	// this presentation, so the counter bump lands right after the banner leaves.
	import { onMount } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';
	import { MainContainer } from 'components-layout';
	import { waitForTimeout } from 'utils-shared/wait';

	import { SYMBOL_SIZE } from '../game/constants';
	import { getContext } from '../game/context';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor } from '../game/motion';
	import PrismPanel from './PrismPanel.svelte';

	const context = getContext();

	const GOLD = 0xffd25e;
	const BOX_W = SYMBOL_SIZE * 3.7;
	const BOX_H = SYMBOL_SIZE * 1.9;

	let extraSpins = $state(0);
	let visible = $state(false);
	let leaving = $state(false);
	let nowMs = $state(0);
	let shownAt = 0;
	let leaveAt = 0;

	onMount(() => {
		let raf = 0;
		const frame = () => {
			nowMs = performance.now();
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	context.eventEmitter.subscribeOnMount({
		retriggerShow: async (emitterEvent) => {
			extraSpins = emitterEvent.extraSpins;
			leaving = false;
			visible = true;
			shownAt = performance.now();
			// pop (360ms) + read hold — the whole beat stays under 1.6s so autoplay pacing
			// never drags; the scatter fanfare is still ringing over it
			await waitForTimeout(1260);
			leaving = true;
			leaveAt = performance.now();
			await waitForTimeout(240);
			visible = false;
		},
	});

	const inU = $derived(clamp01((nowMs - shownAt) / 360));
	const outU = $derived(leaving ? clamp01((nowMs - leaveAt) / 240) : 0);
	const scale = $derived.by(() => {
		if (leaving) return 1 - 0.18 * EASE.collapse(outU);
		return 0.7 + 0.3 * EASE.impact(inU);
	});
	const alpha = $derived(leaving ? 1 - EASE.collapse(outU) : clamp01(inU * 2.4));
	const secs = $derived(nowMs / 1000);
</script>

{#if visible}
	<MainContainer>
		<Container
			x={context.stateGameDerived.boardLayout().x}
			y={context.stateGameDerived.boardLayout().y}
			{scale}
			{alpha}
		>
			<!-- soft gold bloom so the plaque sits IN the scene, not pasted on it -->
			<Graphics
				blendMode="add"
				draw={(g) => {
					const bloom = EASE.settle(inU);
					for (let i = 3; i >= 1; i--) {
						const u = i / 3;
						g.circle(0, 0, SYMBOL_SIZE * 2.1 * u * bloom).fill({
							color: lerpColor(GOLD, 0xffffff, 0.3),
							alpha: 0.05 * (1.15 - u),
						});
					}
				}}
			/>
			<PrismPanel width={BOX_W} height={BOX_H} accent={GOLD}>
				<Container y={-SYMBOL_SIZE * 0.28}>
					<ResponsiveBitmapText
						anchor={0.5}
						maxWidth={BOX_W - SYMBOL_SIZE * 0.6}
						text={`+${extraSpins}`}
						style={prismStyle(SYMBOL_SIZE * 0.98, { align: 'center' })}
					/>
				</Container>
				<Container y={SYMBOL_SIZE * 0.52}>
					<ResponsiveBitmapText
						anchor={0.5}
						maxWidth={BOX_W - SYMBOL_SIZE * 0.5}
						text="FREE SPINS"
						style={superLabelStyle(SYMBOL_SIZE * 0.34)}
					/>
				</Container>
				<!-- twin scatter sparks orbiting the +N — ties the banner to what earned it -->
				<Graphics
					blendMode="add"
					draw={(g) => {
						for (const dir of [-1, 1]) {
							const ang = secs * 1.6 * dir + (dir > 0 ? 0 : Math.PI);
							const x = Math.cos(ang) * BOX_W * 0.36;
							const y = -SYMBOL_SIZE * 0.28 + Math.sin(ang) * SYMBOL_SIZE * 0.3;
							const tw = (Math.sin(secs * Math.PI * 3 + dir) + 1) / 2;
							const r = 2 + 2.6 * tw;
							g.poly([x, y - r, x + r, y, x, y + r, x - r, y]).fill({
								color: lerpColor(GOLD, 0xffffff, 0.5),
								alpha: 0.35 + 0.45 * tw,
							});
						}
					}}
				/>
			</PrismPanel>
		</Container>
	</MainContainer>
{/if}
