<script lang="ts">
	import { onMount } from 'svelte';

	import { EnablePixiExtension } from 'components-pixi';
	import { EnableHotkey } from 'components-shared';
	import { MainContainer } from 'components-layout';
	import { App, Sprite, REM } from 'pixi-svelte';
	import { stateModal } from 'state-shared';

	import { UI, UiGameName } from 'components-ui-pixi';
	import { GameVersion, Modals } from 'components-ui-html';

	import { stateMeta } from 'state-shared';

	import { getContext } from '../game/context';
	import { PRISM_BET_MODE_META } from '../game/betModeMeta';
	import config from '../game/config';
	import EnableSound from './EnableSound.svelte';
	import EnableGameActor from './EnableGameActor.svelte';
	import ResumeBet from './ResumeBet.svelte';
	import Sound from './Sound.svelte';
	import Background from './Background.svelte';
	import SuperStudiosBoot from './SuperStudiosBoot.svelte';
	import BoardFrame from './BoardFrame.svelte';
	import Board from './Board.svelte';
	import Anticipations from './Anticipations.svelte';
	import Win from './Win.svelte';
	import FreeSpinIntro from './FreeSpinIntro.svelte';
	import FreeSpinCounter from './FreeSpinCounter.svelte';
	import RetriggerBanner from './RetriggerBanner.svelte';
	import FreeSpinOutro from './FreeSpinOutro.svelte';
	import Transition from './Transition.svelte';

	const context = getContext();

	// Prism Path bet modes (BASE / DRAGON BONUS 100x / SUPER DRAGON BONUS 300x) drive the
	// buy modal cards and the RGS bet mode string.
	stateMeta.betModeMeta = PRISM_BET_MODE_META;

	// Paytable/rules content (MUST mirror math/games/prism_path/game_config.py).
	// STATIC LITERAL new URL(...) per symbol — the ONLY form Vite rewrites reliably
	// here. A dynamic template resolved to undefined, and import.meta.glob cannot
	// reach the served static/ dir (audit: all 18 paytable/rules images shipped
	// broken). This is the same proven pattern game/assets.ts uses.
	const SYM_URLS: Record<string, string> = {
		WILD: new URL('../../assets/symbols/WILD.png', import.meta.url).href,
		WILDSTICKY: new URL('../../assets/symbols/WILDSTICKY.png', import.meta.url).href,
		SCAT: new URL('../../assets/symbols/SCAT.png', import.meta.url).href,
		H1: new URL('../../assets/symbols/H1.png', import.meta.url).href,
		H2: new URL('../../assets/symbols/H2.png', import.meta.url).href,
		H3: new URL('../../assets/symbols/H3.png', import.meta.url).href,
		H4: new URL('../../assets/symbols/H4.png', import.meta.url).href,
		L2: new URL('../../assets/symbols/L2.png', import.meta.url).href,
		L3: new URL('../../assets/symbols/L3.png', import.meta.url).href,
		L4: new URL('../../assets/symbols/L4.png', import.meta.url).href,
		L5: new URL('../../assets/symbols/L5.png', import.meta.url).href,
		beastRight: new URL('../../assets/symbols/beastRight.png', import.meta.url).href,
	};
	const symImg = (name: string) => SYM_URLS[name] ?? '';

	// ---- Paytable DERIVED from src/game/config.ts (the frontend mirror of
	// math/games/prism_path/game_config.py PAYTABLE_PM) so display can never drift ----
	const fmtX = (value: number) => `${parseFloat(value.toFixed(2))}x`;
	const PAY_ORDER = ['WILD', 'H1', 'H2', 'H3', 'H4', 'L2', 'L3', 'L4', 'L5'] as const;
	const PAYS = PAY_ORDER.map((key) => {
		const byKind = Object.assign({}, ...config.symbols[key].paytable) as Record<
			'3' | '4' | '5',
			number
		>;
		return { key, p: [fmtX(byKind['5']), fmtX(byKind['4']), fmtX(byKind['3'])] };
	});

	// Scatter -> free spins (trigger / free-game retrigger, mirrors the math tables)
	const SCATTER_AWARDS = [
		{ count: 3, spins: 8, retrigger: 5 },
		{ count: 4, spins: 12, retrigger: 8 },
		{ count: 5, spins: 15, retrigger: 12 },
	];

	// 17 line shapes straight from config (row index per reel), drawn as mini 5x5 boards
	const PAYLINES = Array.from(
		{ length: 17 },
		(_, index) => config.paylines[`${index + 1}` as keyof typeof config.paylines],
	);
	const RULES = [
		{
			img: symImg('WILD'),
			title: 'DRAGON WILD',
			text: 'The Prism Dragon is WILD and substitutes for all symbols except the Scatter. A landing dragon faces a random direction and FIRES a path of multiplier wilds (x2, x3, x5 — up to x10 in free spins) from its square to the board edge. A dragon facing the edge fires off the board. A run of only wilds on a payline pays at gem tier — a full dragon path across a line IS a winning line.',
		},
		{
			img: symImg('beastRight'),
			title: 'CROSSING PATHS MULTIPLY',
			text: 'Each dragon counts ONCE per winning line. When the paths of two or more dragons cross on a line, their multipliers MULTIPLY together (x2 crossed with x3 pays x6).',
		},
		{
			img: symImg('WILDSTICKY'),
			title: 'STICKY DRAGONS (FREE SPINS)',
			text: 'During FREE SPINS a landing dragon may become STICKY: it claims its square (marked with a glowing border) and re-lands there on every remaining free spin, firing a fresh path in a new direction each time while keeping its multiplier. Up to 2 dragons can be sticky at once.',
		},
		{
			img: symImg('SCAT'),
			title: 'FREE SPINS',
			text: '3, 4 or 5 Scatters award 8, 12 or 15 FREE SPINS with an enhanced chance of dragons. During free spins, 3, 4 or 5 Scatters retrigger 5, 8 or 12 additional spins. DRAGON BONUS (100x bet) buys free spins entry. SUPER DRAGON BONUS (300x bet) buys free spins where a dragon is GUARANTEED every spin, with a much higher sticky-dragon chance.',
		},
		// feature-spin modes — costs sourced from betModeMeta so rules copy can't drift
		{
			img: PRISM_BET_MODE_META.HUNT.assets.icon,
			title: 'BONUS HUNT',
			text: `Activate BONUS HUNT to hunt the feature: every spin costs ${fmtX(PRISM_BET_MODE_META.HUNT.costMultiplier)} bet and carries 4x THE CHANCE of triggering FREE SPINS. All other rules are unchanged — dragons, paths and paylines play exactly as normal. Deactivate at any time.`,
		},
		{
			img: PRISM_BET_MODE_META.DRAGON3.assets.icon,
			title: 'TRIPLE DRAGONS',
			text: `Buy a single spin with THREE Prism Dragons GUARANTEED for ${fmtX(PRISM_BET_MODE_META.DRAGON3.costMultiplier)} bet. Every dragon fires a path of multiplier wilds — crossing paths MULTIPLY together. Scatters still land naturally, so the spin can also trigger FREE SPINS.`,
		},
		{
			img: PRISM_BET_MODE_META.DRAGON5.assets.icon,
			title: 'DRAGON STORM',
			text: `Buy a single spin with FIVE Prism Dragons GUARANTEED for ${fmtX(PRISM_BET_MODE_META.DRAGON5.costMultiplier)} bet. Paths of multiplier wilds tear across the board and every crossing MULTIPLIES — the most explosive single spin in the game. Scatters still land naturally, so the spin can also trigger FREE SPINS.`,
		},
	];

	onMount(() => (context.stateLayout.showLoadingScreen = true));

	context.eventEmitter.subscribeOnMount({
		buyBonusConfirm: () => {
			stateModal.modal = { name: 'buyBonusConfirm' };
		},
	});
</script>

<App>
	<EnableSound />
	<EnableHotkey />
	<EnableGameActor />
	<EnablePixiExtension />

	<Background />

	<!-- boot (Super Studios loader -> Prism Path intro) is a DOM overlay below; while it
	     is up the canvas shows only the background sky behind it -->
	{#if !context.stateLayout.showLoadingScreen}
		<ResumeBet />
		<!--
			The reason why <Sound /> is rendered after clicking the loading screen:
			"Autoplay with sound is allowed if: The user has interacted with the domain (click, tap, etc.)."
			Ref: https://developer.chrome.com/blog/autoplay
		-->
		<Sound />

		<MainContainer>
			<BoardFrame />
		</MainContainer>

		<MainContainer>
			<Board />
			<Anticipations />
		</MainContainer>

		<UI>
			{#snippet gameName()}
				<UiGameName name="PRISM PATH" />
			{/snippet}
			{#snippet logo()}
				<!-- new wordmark art is 640x395; portrait renders smaller so the mark never
				     eats ~30% of a phone's width (audit), with a small top inset -->
				{@const logoW = context.stateLayoutDerived.layoutType() === 'portrait' ? REM * 4.6 : REM * 7}
				<Sprite key="logo" anchor={{ x: 1, y: 0 }} y={10} width={logoW} height={logoW * (395 / 640)} />
			{/snippet}
		</UI>
		<Win />
		<FreeSpinIntro />
		{#if ['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType())}
			<FreeSpinCounter />
		{/if}
		<RetriggerBanner />
		<FreeSpinOutro />
		<Transition />
	{/if}
</App>

<!-- DOM boot overlay: Super Studios loader (driven by real asset progress), then the
     Prism Path intro splash. The CONTINUE click is the audio-unlock gesture, so Sound
     mounts right after it exactly as before. -->
{#if context.stateLayout.showLoadingScreen}
	<SuperStudiosBoot onenter={() => (context.stateLayout.showLoadingScreen = false)} />
{/if}

<Modals>
	{#snippet version()}
		<GameVersion version="1.0.0" />
	{/snippet}
	{#snippet payTable()}
		<div class="prism-rules">
			<h2>PAYTABLE</h2>
			<p class="note">Wins pay on 17 fixed lines, left to right, from the leftmost reel. Line win = symbol pay × total bet × dragon multipliers. Wilds always extend the line through the symbol that completes it; a line of only wilds pays at gem tier. One win per line. Maximum win: 5,000x total bet.</p>
			<div class="pay-grid">
				{#each PAYS as s (s.key)}
					<div class="pay-cell">
						<img src={symImg(s.key)} alt={s.key} />
						<div class="pays">
							<div>5&nbsp;—&nbsp;{s.p[0]}</div>
							<div>4&nbsp;—&nbsp;{s.p[1]}</div>
							<div>3&nbsp;—&nbsp;{s.p[2]}</div>
						</div>
					</div>
				{/each}
				<!-- scatter pays free spins, not line wins -->
				<div class="pay-cell pay-cell-scatter">
					<img src={symImg('SCAT')} alt="SCATTER" />
					<div class="pays">
						{#each SCATTER_AWARDS as award (award.count)}
							<div>{award.count}&nbsp;—&nbsp;{award.spins} FREE SPINS</div>
						{/each}
						<div class="scatter-retrigger">
							Retrigger in free game: 3 / 4 / 5 Scatters award +{SCATTER_AWARDS[0]
								.retrigger} / +{SCATTER_AWARDS[1].retrigger} / +{SCATTER_AWARDS[2].retrigger} spins.
						</div>
					</div>
				</div>
			</div>

			<h2>PAYLINES</h2>
			<p class="note">All wins pay left to right on these 17 fixed lines.</p>
			<div class="lines-grid">
				{#each PAYLINES as line, index (index)}
					<div class="line-cell">
						<div class="mini-board" aria-label="payline {index + 1}">
							{#each Array.from({ length: 25 }) as _, cell (cell)}
								<div class="mini-cell" class:on={line[cell % 5] === Math.floor(cell / 5)}></div>
							{/each}
						</div>
						<div class="line-num">{index + 1}</div>
					</div>
				{/each}
			</div>
		</div>
	{/snippet}
	{#snippet gameRules()}
		<div class="prism-rules">
			<h2>GAME RULES</h2>
			{#each RULES as r (r.title)}
				<div class="rule">
					<img src={r.img} alt="" />
					<div>
						<h3>{r.title}</h3>
						<p>{r.text}</p>
					</div>
				</div>
			{/each}
			<p class="note">RTP 96.5%. Malfunction voids all pays and plays. Outcomes are determined by the certified remote game server.</p>
		</div>
	{/snippet}
</Modals>

<style>
	/* type hierarchy: Prism (Chango) = headings only, Superui (Fredoka) = body voice.
	   All body sizes stay >= 0.875rem => >= 12.25px at the 14px phone root. */
	.prism-rules {
		color: #fff;
		max-width: 640px;
		text-align: left;
		font-family: 'Superui', sans-serif;
	}
	.prism-rules h2,
	.prism-rules h3 {
		font-family: 'Prism', 'Superui', sans-serif;
		font-weight: 400;
	}
	.prism-rules h2 {
		text-align: center;
		letter-spacing: 0.06em;
	}
	.prism-rules .note {
		opacity: 0.85;
		font-size: 0.875rem;
		text-align: center;
	}
	.pay-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.6rem;
	}
	@media screen and (max-width: 640px) {
		.pay-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
	.pay-cell {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		background: rgba(255, 255, 255, 0.06);
		border-radius: 10px;
		padding: 0.4rem;
	}
	.pay-cell img {
		width: 52px;
		height: 52px;
		object-fit: contain;
		flex: 0 0 auto;
	}
	.pay-cell .pays {
		font-size: 0.875rem;
		line-height: 1.3;
		white-space: nowrap;
	}
	/* scatter spans the full row: its lines are longer than a gem cell's */
	.pay-cell-scatter {
		grid-column: 1 / -1;
	}
	.scatter-retrigger {
		white-space: normal;
		opacity: 0.85;
		margin-top: 0.2rem;
	}
	.lines-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
		gap: 0.6rem;
	}
	.line-cell {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.3rem;
		background: rgba(255, 255, 255, 0.06);
		border-radius: 10px;
		padding: 0.45rem 0.3rem;
	}
	.mini-board {
		display: grid;
		grid-template-columns: repeat(5, 9px);
		grid-auto-rows: 9px;
		gap: 2px;
	}
	.mini-cell {
		background: rgba(191, 233, 255, 0.14);
		border-radius: 2px;
	}
	.mini-cell.on {
		background: #ffd25e;
		box-shadow: 0 0 5px rgba(255, 210, 94, 0.55);
	}
	.line-num {
		font-family: 'Prism', 'Superui', sans-serif;
		font-size: 0.875rem;
		color: #fff4dc;
	}
	.rule {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		margin: 0.7rem 0;
	}
	.rule img {
		width: 72px;
		height: 72px;
		object-fit: contain;
		flex: 0 0 auto;
	}
	.rule h3 {
		margin: 0 0 0.2rem;
	}
	.rule p {
		margin: 0;
		font-size: 0.9rem;
		opacity: 0.92;
	}
</style>
