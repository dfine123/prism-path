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
	const symImg = (name: string) => new URL(`../../assets/symbols/${name}.png`, import.meta.url).href;
	const PAYS = [
		{ key: 'WILD', p: ['5x', '1.5x', '0.5x'] },
		{ key: 'H1', p: ['5x', '1.5x', '0.5x'] },
		{ key: 'H2', p: ['5x', '1.5x', '0.5x'] },
		{ key: 'H3', p: ['5x', '1.5x', '0.5x'] },
		{ key: 'H4', p: ['5x', '1.5x', '0.5x'] },
		{ key: 'L2', p: ['1x', '0.5x', '0.25x'] },
		{ key: 'L3', p: ['1x', '0.5x', '0.25x'] },
		{ key: 'L4', p: ['1x', '0.5x', '0.25x'] },
		{ key: 'L5', p: ['1x', '0.5x', '0.25x'] },
	];
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
			text: 'During FREE SPINS a landing dragon may become STICKY: it claims its square (marked with a glowing border) and re-lands there on every remaining free spin, firing a fresh path in a new direction each time while keeping its multiplier.',
		},
		{
			img: symImg('SCAT'),
			title: 'FREE SPINS',
			text: '3, 4 or 5 Scatters award 8, 12 or 15 FREE SPINS with an enhanced chance of dragons. During free spins, 3, 4 or 5 Scatters retrigger 5, 8 or 12 additional spins. DRAGON BONUS (100x bet) buys free spins entry. SUPER DRAGON BONUS (300x bet) buys free spins where a dragon is GUARANTEED every spin, with a much higher sticky-dragon chance.',
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
				<Sprite key="logo" anchor={{ x: 1, y: 0 }} width={REM * 7} height={REM * 6.6} />
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
		<GameVersion version="0.0.0" />
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
	.prism-rules {
		color: #fff;
		max-width: 640px;
		text-align: left;
	}
	.prism-rules h2 {
		text-align: center;
		letter-spacing: 0.06em;
	}
	.prism-rules .note {
		opacity: 0.8;
		font-size: 0.85rem;
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
	}
	.pay-cell .pays {
		font-size: 0.8rem;
		line-height: 1.25;
		white-space: nowrap;
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
