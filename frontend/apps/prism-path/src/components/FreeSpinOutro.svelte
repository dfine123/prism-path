<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventFreeSpinOutro =
		| { type: 'freeSpinOutroShow' }
		| { type: 'freeSpinOutroHide' }
		| { type: 'freeSpinOutroCountUp'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	// Feature finale — BONUS-THEMED closing ceremony on the gold ART PLAQUE (same plate
	// family as the intro; crown crest and seated gems baked into the art). The total is
	// shown STATIC — "(bonus name) COMPLETE" / "TOTAL WIN:" / amount — with one impact
	// beat instead of a rolling count-up (the roll ceremony belongs to the wins inside
	// the feature). Shard burst behind, press (or autoplay) to return to the day realm.
	import { onMount } from 'svelte';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';
	import { BitmapText, Container, Graphics, Sprite } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';
	import { FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor } from '../game/motion';
	import { boardFocusTo } from '../game/stateFx.svelte';
	import PrismShards from './PrismShards.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	const GOLD = 0xffd25e;
	// gold plate art is 1324x742
	const PLATE_W = SYMBOL_SIZE * 7.15;
	const PLATE_H = PLATE_W * (742 / 1324);
	const BODY_DY = PLATE_H * 0.035;
	const CUT = PLATE_H * 0.14;

	const octagon = (w: number, h: number): number[] => {
		const w2 = w / 2;
		const h2 = h / 2;
		const c = CUT;
		return [-w2 + c, -h2, w2 - c, -h2, w2, -h2 + c, w2, h2 - c, w2 - c, h2, -w2 + c, h2, -w2, h2 - c, -w2, -h2 + c];
	};
	const scaleOct = (pts: number[], sc: number) => pts.map((v) => v * sc);

	// gem seats on the gold plate art (fractions of plate W/H from its center)
	const GLINTS: Array<[number, number]> = [
		[-0.43, -0.32], [0.43, -0.32],
		[-0.447, 0.0], [0.447, 0.0],
		[-0.42, 0.37], [0.42, 0.37],
		[0, 0.4], [0, -0.44],
	];

	// "(bonus name) COMPLETE": bought features carry their card title; a naturally
	// triggered (or hunt-found) feature is plainly FREE SPINS
	const bonusName = $derived.by(() => {
		const mode = stateBetDerived.activeBetMode() as { type?: string; title?: string } | null;
		return mode?.type === 'buy' && mode.title ? mode.title : 'FREE SPINS';
	});

	// starts HIDDEN like every other overlay — init true made the first feature's panel
	// hard-cut in (FadeContainer had already tweened to alpha 1 invisibly at boot)
	let show = $state(false);
	let amount = $state(0);
	let oncomplete = $state(() => {});
	let shownAtMs = 0;
	let nowMs = $state(0);

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
		freeSpinOutroShow: () => {
			shownAtMs = performance.now();
			show = true;
		},
		freeSpinOutroHide: async () => (show = false),
		// same awaited contract; the amount is shown STATIC (no roll), the level unused
		freeSpinOutroCountUp: async (emitterEvent) => {
			amount = emitterEvent.amount;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});

	// camera focus while the panel holds (same as the big-win box)
	$effect(() => {
		boardFocusTo(show ? 1 : 0);
	});

	const secs = $derived(nowMs / 1000);
	const age = $derived(show ? (nowMs - shownAtMs) / 1000 : 0);
	const plateIn = $derived(clamp01(age / 0.42));
	const plateScale = $derived.by(() => {
		if (plateIn < 1) return 1.22 - 0.22 * EASE.impact(plateIn);
		return 1 + 0.005 * Math.sin(secs * Math.PI * 0.9);
	});
	const plateAlpha = $derived(clamp01(age / 0.15));
	const wAge = $derived(clamp01((age - 0.14) / 0.34));
	const labelAge = $derived(clamp01((age - 0.3) / 0.3));
	// the amount lands STATIC with one impact beat just after the wordmark (no roll)
	const amountIn = $derived(clamp01((age - 0.4) / 0.32));
	const amountScale = $derived.by(() => {
		if (amountIn < 1) return 2.0 - 1.0 * EASE.impact(amountIn);
		return 1 + 0.015 * Math.sin(secs * Math.PI * 1.4);
	});
	const burstU = $derived(clamp01((age - 0.48) / 0.55));
	// the shard burst is the celebration garnish: a short eruption as the panel lands
	const bursting = $derived(show && age < 1.4);
</script>

<FadeContainer {show}>
	{#if show}
		<!-- manual play holds on PRESS TO CONTINUE; under AUTOPLAY or an active SPACE-HOLD
		     the panel auto-advances after a readable hold (a held key can never produce
		     the fresh keydown PressToContinue needs). Generation-guarded. -->
		<OnMount
			onmount={async () => {
				const myResolve = oncomplete;
				if (stateBetDerived.hasAutoBetCounter() || stateBet.isSpaceHold) {
					await waitForTimeout(1700);
					if (oncomplete === myResolve) oncomplete();
				}
			}}
		/>

		<CanvasSizeRectangle backgroundColor={0x05030a} backgroundAlpha={0.6} />

		<!-- shards UNDER the panel: gems erupt from behind the plaque, never over text -->
		<PrismShards emit={bursting} levelAlias="big" />

		<MainContainer>
			<Container
				x={context.stateGameDerived.boardLayout().x}
				y={context.stateGameDerived.boardLayout().y}
			>
				<!-- soft gold backdrop bloom (textured gaussian falloff, never a flat disc) -->
				<Sprite
					key="mote"
					anchor={0.5}
					blendMode="add"
					tint={lerpColor(GOLD, 0xffffff, 0.25)}
					width={SYMBOL_SIZE * 9.6 * (0.92 + 0.08 * Math.sin(secs * Math.PI * 0.8))}
					height={SYMBOL_SIZE * 7 * (0.92 + 0.08 * Math.sin(secs * Math.PI * 0.8))}
					alpha={0.26 * plateAlpha}
				/>

				<Container scale={plateScale} alpha={plateAlpha}>
					<!-- THE PLATE: gold crystal plaque art (crown crest + seated gems baked in) -->
					<Sprite key="plateGold" anchor={0.5} width={PLATE_W} height={PLATE_H} />

					<!-- "(bonus name) COMPLETE" drops in with the impact settle. ROW RHYTHM
					     (measured off the art, fractions of PLATE_H): crown intrudes to
					     -0.259, interior bottom +0.358 — title -0.15 / label +0.03 /
					     amount +0.20 keeps every row inside the glass -->
					<Container
						y={-PLATE_H * 0.15 - SYMBOL_SIZE * 0.3 * (1 - EASE.settle(wAge))}
						alpha={clamp01(wAge * 2.2)}
						scale={1.25 - 0.25 * EASE.impact(wAge)}
					>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={PLATE_W * 0.62}
							text={`${bonusName} COMPLETE`}
							style={prismStyle(SYMBOL_SIZE * 0.55, { align: 'center' })}
						/>
					</Container>

					<Container y={PLATE_H * 0.015} alpha={labelAge}>
						<BitmapText
							anchor={0.5}
							text="TOTAL WIN:"
							style={superLabelStyle(SYMBOL_SIZE * 0.26, { align: 'center' })}
						/>
					</Container>

					<!-- pool of light under the amount -->
					<Sprite
						key="mote"
						anchor={0.5}
						blendMode="add"
						tint={lerpColor(GOLD, 0xffffff, 0.3)}
						y={PLATE_H * 0.175}
						width={SYMBOL_SIZE * 3.4}
						height={SYMBOL_SIZE * 2.0}
						alpha={0.28 + 0.25 * (1 - burstU) + 0.05 * Math.sin(secs * Math.PI * 1.1)}
					/>

					<!-- base size is set for SHORT amounts ("$47.75") — the responsive fit
					     only ever SHRINKS long strings, so the base size is what a short
					     amount actually renders at; 1.0S crowded the bottom inlay -->
					<Container y={PLATE_H * 0.175} scale={amountScale} alpha={clamp01(amountIn * 2.4)}>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={PLATE_W * 0.68}
							text={bookEventAmountToCurrencyString(amount)}
							style={prismStyle(SYMBOL_SIZE * 0.82, { align: 'center', letterSpacing: 0 })}
						/>
					</Container>

					<!-- glint burst thrown from the amount as it lands -->
					{#if burstU > 0 && burstU < 1}
						{#each Array.from({ length: 6 }, (_, i) => i) as i (i)}
							{@const a = (i / 6) * Math.PI * 2 + 0.4}
							{@const r = SYMBOL_SIZE * (0.5 + 1.7 * EASE.settle(burstU))}
							<Sprite
								key="moteStar"
								anchor={0.5}
								blendMode="add"
								tint={lerpColor(GOLD, 0xffffff, 0.6)}
								x={Math.cos(a) * r * 1.25}
								y={PLATE_H * 0.175 + Math.sin(a) * r * 0.7}
								width={SYMBOL_SIZE * 0.34 * (1 - burstU * 0.6)}
								height={SYMBOL_SIZE * 0.34 * (1 - burstU * 0.6)}
								rotation={a + burstU * 1.2}
								alpha={0.85 * (1 - burstU)}
							/>
						{/each}
					{/if}

					<!-- the frame's gems catch light: slow, staggered -->
					{#each GLINTS as [gx, gy], i (i)}
						{@const tw = Math.max(0, Math.sin(secs * Math.PI * 0.5 + i * 1.9))}
						<Sprite
							key="moteStar"
							anchor={0.5}
							blendMode="add"
							tint={0xffffff}
							x={gx * PLATE_W}
							y={gy * PLATE_H}
							width={SYMBOL_SIZE * 0.42 * (0.7 + 0.3 * tw)}
							height={SYMBOL_SIZE * 0.42 * (0.7 + 0.3 * tw)}
							rotation={i * 0.7}
							alpha={0.5 * Math.pow(tw, 3)}
						/>
					{/each}

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

				<!-- landing shockwave: the plate body's silhouette bursting outward, twin rings -->
				{#if age > 0 && age < 0.62}
					<Graphics
						blendMode="add"
						draw={(g) => {
							const base = octagon(PLATE_W, PLATE_H * 0.92);
							const s1 = clamp01(age / 0.5);
							g.poly(scaleOct(base, 1 + 0.85 * EASE.settle(s1))).stroke({
								width: 3 + 10 * (1 - s1),
								color: lerpColor(0xffffff, GOLD, s1),
								alpha: 0.5 * (1 - s1),
								join: 'miter',
							});
							const s2 = clamp01((age - 0.09) / 0.5);
							if (s2 > 0) {
								g.poly(scaleOct(base, 1 + 0.5 * EASE.settle(s2))).stroke({
									width: 2 + 6 * (1 - s2),
									color: GOLD,
									alpha: 0.35 * (1 - s2),
									join: 'miter',
								});
							}
						}}
						y={BODY_DY}
					/>
				{/if}
			</Container>
		</MainContainer>

		<!-- unmount the full-screen catcher the instant hiding starts — an invisible
		     fading rect must not swallow board presses -->
		<PressToContinue showLabel={false} onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
