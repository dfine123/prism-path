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

	setContext();

	const play = (book: { events: unknown[] }) => async () => {
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
