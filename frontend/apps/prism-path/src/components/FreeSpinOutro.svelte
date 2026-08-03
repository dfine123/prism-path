<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventFreeSpinOutro =
		| { type: 'freeSpinOutroShow' }
		| { type: 'freeSpinOutroHide' }
		| { type: 'freeSpinOutroCountUp'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	// Feature finale — BONUS-THEMED closing panel (operator direction 2026-08-03): the
	// total is shown STATIC — "(bonus name) COMPLETE" / "TOTAL WIN:" / amount — with one
	// impact beat instead of a rolling count-up (the roll ceremony belongs to the wins
	// inside the feature). Gold plaque in the game's crystal language, shard burst
	// behind, press (or autoplay) to return to the day realm.
	import { onMount } from 'svelte';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';
	import { Container, Graphics } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';
	import { FadeContainer } from 'components-pixi';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { EASE, clamp01, lerpColor, paletteAt } from '../game/motion';
	import { boardFocusTo } from '../game/stateFx.svelte';
	import PrismPanel from './PrismPanel.svelte';
	import PrismShards from './PrismShards.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();

	const GOLD = 0xffd25e;
	const BOX_W = SYMBOL_SIZE * 6.0;
	const BOX_H = SYMBOL_SIZE * 3.4;

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

	const age = $derived(show ? (nowMs - shownAtMs) / 1000 : 0);
	const intro = $derived(clamp01(age / 0.42));
	const wordScale = $derived.by(() => {
		if (intro < 1) return 1.9 - 0.9 * EASE.impact(intro);
		return 1 + 0.015 * Math.sin(age * Math.PI * 1.5);
	});
	const boxScale = $derived(0.86 + 0.14 * EASE.impact(clamp01(age / 0.36)));
	// the amount lands STATIC with one impact beat just after the wordmark (no roll)
	const amountIn = $derived(clamp01((age - 0.34) / 0.3));
	const amountScale = $derived.by(() => {
		if (amountIn < 1) return EASE.impact(amountIn);
		return 1 + 0.018 * Math.sin(age * Math.PI * 1.4);
	});
	const amountAlpha = $derived(clamp01(amountIn * 2.4));
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
				scale={boxScale}
			>
				<!-- gold rays: the bonus's own light, quieter than a win ceremony -->
				<Graphics
					blendMode="add"
					draw={(g) => {
						const bloom = EASE.settle(clamp01(age / 0.55));
						const R = SYMBOL_SIZE * 4.2;
						for (let i = 0; i < 10; i++) {
							const a0 = age * 0.14 + (i / 10) * Math.PI * 2;
							const w = (Math.PI * 2 / 10) * 0.36;
							const pulse = 0.6 + 0.4 * Math.sin(age * Math.PI * 1.3 + i);
							g.moveTo(0, 0)
								.arc(0, 0, R * bloom, a0 - w / 2, a0 + w / 2)
								.lineTo(0, 0)
								.fill({ color: lerpColor(GOLD, paletteAt(i / 10), 0.2), alpha: 0.06 * pulse * bloom });
						}
						g.circle(0, 0, SYMBOL_SIZE * 2.2 * bloom).fill({
							color: lerpColor(GOLD, 0xffffff, 0.35),
							alpha: 0.1 + 0.04 * Math.sin(age * Math.PI * 1.2),
						});
					}}
				/>

				<PrismPanel width={BOX_W} height={BOX_H} accent={GOLD}>
					<Container y={-SYMBOL_SIZE * 0.95} scale={wordScale} alpha={clamp01(intro * 2.2)}>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={BOX_W - SYMBOL_SIZE * 0.9}
							text={`${bonusName} COMPLETE`}
							style={prismStyle(SYMBOL_SIZE * 0.82, { align: 'center' })}
						/>
					</Container>
					<Container y={-SYMBOL_SIZE * 0.06} alpha={amountAlpha}>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={BOX_W - SYMBOL_SIZE * 1.2}
							text="TOTAL WIN:"
							style={superLabelStyle(SYMBOL_SIZE * 0.34)}
						/>
					</Container>
					<Container y={SYMBOL_SIZE * 0.82} scale={amountScale} alpha={amountAlpha}>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={BOX_W - SYMBOL_SIZE * 1.0}
							text={bookEventAmountToCurrencyString(amount)}
							style={prismStyle(SYMBOL_SIZE * 1.2, { align: 'center', letterSpacing: 0 })}
						/>
					</Container>
				</PrismPanel>
			</Container>
		</MainContainer>

		<!-- unmount the full-screen catcher the instant hiding starts — an invisible
		     fading rect must not swallow board presses -->
		<PressToContinue onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
