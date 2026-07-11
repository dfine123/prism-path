<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'MODE_PRISM/scenario',
	});
</script>

<script lang="ts">
	import {
		StoryGameTemplate,
		StoryLocale,
		type TemplateArgs,
		templateArgs,
	} from 'components-storybook';

	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';
	import { playBet } from '../game/utils';
	import { scenarios } from './data/scenarios';
	import baseBooks from './data/base_books';
	import bonusBooks from './data/bonus_books';
	import superBooks from './data/super_books';

	setContext();

	const play = (book: { events: unknown[] }) => async () => {
		await playBet({ ...book, state: book.events } as never);
	};

	// Pull a different REAL book on every click -> varied boards, symbols, wins, beasts,
	// free-spin triggers. This is the closest thing to live play in storybook.
	const playRandom = (books: { events: unknown[] }[]) => async () => {
		const book = books[Math.floor(Math.random() * books.length)];
		await playBet({ ...book, state: book.events } as never);
	};

	// Bias toward books that actually do something (skip the pure-zero spins) so the feature
	// is easy to see while dialing in. Falls back to any book if none match.
	const playRandomWin = (books: { payoutMultiplier?: number; events: unknown[] }[]) => async () => {
		const winners = books.filter((b) => (b.payoutMultiplier ?? 0) > 0);
		const pool = winners.length ? winners : books;
		const book = pool[Math.floor(Math.random() * pool.length)];
		await playBet({ ...book, state: book.events } as never);
	};
</script>

{#snippet template(args: TemplateArgs<any>)}
	<StoryGameTemplate
		skipLoadingScreen={args.skipLoadingScreen}
		action={async () => {
			await args.action?.(args.data);
		}}
	>
		<StoryLocale lang="en">
			<Game />
		</StoryLocale>
	</StoryGameTemplate>
{/snippet}

<Story
	name="Play base game (random spin, click Action to respin)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: playRandom(baseBooks) })}
	{template}
/>

<Story
	name="Play base game (random win, skips dead spins)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: playRandomWin(baseBooks) })}
	{template}
/>

<Story
	name="Play bonus free spins (random)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: playRandom(bonusBooks) })}
	{template}
/>

<Story
	name="Play SUPER bonus (guaranteed dragons, random)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: playRandom(superBooks) })}
	{template}
/>

<Story
	name="overlap (x6 jackpot)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.overlap) })}
	{template}
/>

<Story
	name="single beast (x3)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.single) })}
	{template}
/>

<Story
	name="right-pair (only their 2 cells)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.rightPair) })}
	{template}
/>

<Story
	name="down (column fires down)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.down) })}
	{template}
/>

<Story
	name="up (column fires up)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.up) })}
	{template}
/>

<Story
	name="vertical-overlap (x6 column)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.verticalOverlap) })}
	{template}
/>

<Story
	name="down-pair (only their 2 cells)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.downPair) })}
	{template}
/>

<Story
	name="whiff (edge, no path)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.whiff) })}
	{template}
/>

<Story
	name="near-max (5000x cap)"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.nearMax) })}
	{template}
/>

<Story
	name="zero win"
	args={templateArgs({ skipLoadingScreen: true, data: {}, action: play(scenarios.zero) })}
	{template}
/>
