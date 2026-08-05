<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventWin =
		| { type: 'winShow' }
		| { type: 'winHide' }
		| { type: 'winUpdate'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { FadeContainer, ResponsiveBitmapText } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import {
		bookEventAmountToBetAmountMultiplier,
		bookEventAmountToCurrencyString,
	} from 'utils-shared/amount';
	import { stateBet, stateBetDerived } from 'state-shared';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';

	import PrismShards from './PrismShards.svelte';
	import WinBox from './WinBox.svelte';
	import SmallWinPop from './SmallWinPop.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getContext } from '../game/context';
	import { prismStyle, superLabelStyle } from '../game/fonts';
	import { boardFocusTo, markUserAdvance } from '../game/stateFx.svelte';
	import { trailClock } from '../game/trailClock.svelte';

	const context = getContext();

	let show = $state(false);
	let amount = $state(0);
	let winLevelData = $state<WinLevelData>();
	let oncomplete = $state(() => {});

	// ---- TIER-AWARE STAGED ROLL (replaces the single linear tween) ----
	// One flat tween let a big win ZIP through the low tiers (BIG visible for ~0.1s on
	// an epic roll — choppy). The roll is now piecewise over the win-level bands: every
	// tier the amount passes through gets a guaranteed readable segment, and at each
	// band boundary the number PINS for a beat while the box's promotion impact plays.
	// INTERACTION (operator direction): a press mid-roll advances ONE segment (the next
	// tier lands with its full ceremony, not an instant jump to the end), and a big-win
	// box HOLDS on its final amount until a press dismisses it (autoplay/space-hold
	// auto-advance after a readable beat instead).
	// PROMOTION boundaries only (SUPER/MEGA/EPIC/MAX entry points, book units) — the
	// roll pins exactly where the box promotes; 15x is BIG's floor, not a boundary
	const BOUNDS = [3000, 5000, 10000, 500000];
	const HOLD_MS = 350; // boundary pin while the promotion lands
	const MIN_SEG_MS = 900; // no tier may flash by faster than this

	let countUpAmount = $state(0);
	let countUpCompleted = $state(false);
	let rollToken = 0;
	let advanceReq = { v: false }; // press mid-roll: finish the CURRENT segment only

	const easeInOut = (u: number) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2);

	const tweenSegment = (from: number, to: number, ms: number, token: number) =>
		new Promise<void>((resolve) => {
			const start = performance.now();
			const frame = () => {
				if (token !== rollToken) return resolve();
				if (advanceReq.v) {
					// press: complete THIS segment instantly — the next tier's ceremony
					// still plays at the boundary
					advanceReq.v = false;
					countUpAmount = to;
					return resolve();
				}
				const u = Math.min(1, (performance.now() - start) / ms);
				countUpAmount = Math.round(from + (to - from) * easeInOut(u));
				if (u < 1) requestAnimationFrame(frame);
				else resolve();
			};
			requestAnimationFrame(frame);
		});

	const boundaryHold = async (ms: number, token: number) => {
		const start = performance.now();
		while (performance.now() - start < ms) {
			if (token !== rollToken) return;
			if (advanceReq.v) return; // a queued press chains straight into the next segment
			await waitForTimeout(40);
		}
	};

	const runStagedRoll = async (finalAmount: number, presentMs: number, token: number) => {
		const bounds = BOUNDS.filter((b) => b < finalAmount);
		const targets = [...bounds, finalAmount];
		const rollMs = Math.max(1400, presentMs - bounds.length * HOLD_MS);
		// later segments earn slightly more time (the tension builds, never rushes)
		const weights = targets.map((_, i) => 0.8 + 0.5 * (i / Math.max(1, targets.length - 1)));
		const wSum = weights.reduce((s, w) => s + w, 0);
		let from = 0;
		for (let i = 0; i < targets.length; i++) {
			if (token !== rollToken) break;
			const ms = Math.max(MIN_SEG_MS, (rollMs * weights[i]) / wSum);
			await tweenSegment(from, targets[i], ms, token);
			from = targets[i];
			if (i < targets.length - 1) await boundaryHold(HOLD_MS, token);
		}
		if (token === rollToken) countUpAmount = finalAmount;
	};

	const runPresentation = async () => {
		const myResolve = oncomplete;
		const token = ++rollToken;
		advanceReq = { v: false };
		countUpCompleted = false;
		countUpAmount = 0;

		const rollsUp = bookEventAmountToBetAmountMultiplier(amount) > 10;
		const isBigWin = winLevelData?.type === 'big';
		if (rollsUp && winLevelData) {
			// soft warm ticking under the rolling amount (same loop pattern as
			// sfx_anticipation in Anticipations.svelte) — stopped the moment the roll ends
			context.eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_countup_loop' });
			try {
				await runStagedRoll(amount, winLevelData.presentDuration, token);
			} finally {
				context.eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_countup_loop' });
			}
		} else {
			countUpAmount = amount;
		}
		if (token !== rollToken) return;
		countUpCompleted = true;
		if (isBigWin) {
			// a BIG-WIN box HOLDS until the player dismisses it — except under autoplay
			// or an active space-hold, which auto-advance after a readable beat
			if (stateBetDerived.hasAutoBetCounter() || stateBet.isSpaceHold) {
				await waitForTimeout(1400);
				if (oncomplete === myResolve) oncomplete();
			}
			return; // manual play: PressToContinue resolves
		}
		// an instant amount needs a longer static hold than a rolled one
		await waitForTimeout(rollsUp ? 300 : 650);
		if (oncomplete === myResolve) oncomplete();
	};

	context.eventEmitter.subscribeOnMount({
		winShow: () => (show = true),
		winHide: () => (show = false),
		winUpdate: async (emitterEvent) => {
			amount = emitterEvent.amount;
			winLevelData = emitterEvent.winLevelData;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});

	// camera focus: while the big-win box holds the stage, the board eases back a touch
	$effect(() => {
		boardFocusTo(show && winLevelData?.type === 'big' ? 1 : 0);
	});
</script>

<FadeContainer {show}>
	{#if winLevelData}
		{@const isBigWin = winLevelData.type === 'big'}
		{#if isBigWin}
			<!-- dim veil scales with tier (escalation ladder: banner+dim >= big) -->
			<CanvasSizeRectangle
				backgroundColor={0x05030a}
				backgroundAlpha={0.42 + (winLevelData.level - 6) * 0.06}
			/>
		{/if}

		<!-- one presentation per mount (FadeContainer unmounts at hide, resetting state) -->
		<OnMount onmount={() => void runPresentation()} />

		<!-- shards render UNDER the box — gems erupt from behind the (now opaque) plaque -->
		{#if isBigWin}
			<PrismShards emit={!countUpCompleted} levelAlias={winLevelData?.alias} />
		{/if}

		<MainContainer>
			<Container
				x={context.stateGameDerived.boardLayout().x}
				y={context.stateGameDerived.boardLayout().y}
			>
				{#if isBigWin && winLevelData.text}
					<!-- amount = the LIVE staged roll: the box promotes itself (word, accent,
					     systems, impact stack) exactly at the pinned band boundaries -->
					<WinBox level={winLevelData.level} amount={countUpAmount}>
						<ResponsiveBitmapText
							anchor={0.5}
							maxWidth={SYMBOL_SIZE * 4.6}
							text={bookEventAmountToCurrencyString(countUpAmount)}
							style={prismStyle(SYMBOL_SIZE * 1.3, { align: 'center', letterSpacing: 0 })}
						/>
					</WinBox>
					<!-- the invite seats under the box, and only once the roll has completed
					     and the box truly HOLDS — mid-roll a press means "advance a tier",
					     not "continue" (trailClock ticks: the PressToContinue child holds it) -->
					{#if countUpCompleted}
						<BitmapText
							anchor={0.5}
							y={SYMBOL_SIZE * 2.12}
							text="PRESS ANYWHERE TO CONTINUE"
							alpha={0.62 + 0.38 * (Math.sin(trailClock.t * Math.PI * 1.3) + 1) * 0.5}
							style={superLabelStyle(SYMBOL_SIZE * 0.185, { align: 'center' })}
						/>
					{/if}
				{:else}
					<!-- the MOST COMMON presentation (small wins): same impact vocabulary as
					     every other value in the game, never a flat static paint -->
					<SmallWinPop
						amount={countUpAmount}
						maxWidth={context.stateLayoutDerived.canvasSizes().width /
							context.stateLayoutDerived.mainLayout().scale}
					/>
				{/if}
			</Container>
		</MainContainer>

		<PressToContinue
			showLabel={false}
			onpress={() => {
				if (countUpCompleted) {
					oncomplete();
				} else {
					markUserAdvance(); // promotion lands THIS frame — no anticipation wind-up
					advanceReq.v = true;
				}
			}}
		/>
	{/if}
</FadeContainer>
