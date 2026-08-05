<script lang="ts">
	import { MainContainer, OnPressFullScreen } from 'components-layout';
	import { OnHotkey } from 'components-shared';
	import { BitmapText } from 'pixi-svelte';
	import { stateUi } from 'state-shared';

	import { getContext } from '../game/context';
	import { superLabelStyle } from '../game/fonts';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import { onMount } from 'svelte';

	type Props = {
		onpress: () => void;
		// ceremonies seat the invite line under their own plaque (operator: the
		// screen-bottom label read as disconnected from the box) — they pass false
		// and render the label themselves; the press catcher + hotkey stay here
		showLabel?: boolean;
	};

	const props: Props = $props();
	const context = getContext();

	onMount(() => {
		acquireTrailClock();
		// this overlay owns the screen: the hero bet button's Space handler stands down
		// while it is up, so one press has exactly one meaning
		stateUi.pressCatcherActive = true;
		return () => {
			stateUi.pressCatcherActive = false;
			releaseTrailClock();
		};
	});

	// gentle invite breathe (the screen is never dead)
	const alpha = $derived(0.62 + 0.38 * (Math.sin(trailClock.t * Math.PI * 1.3) + 1) * 0.5);

	// every dismissal press answers with a soft felt tick — confirmation, not fanfare
	const press = () => {
		context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_dismiss' });
		props.onpress();
	};
</script>

{#if props.showLabel ?? true}
	<MainContainer alignVertical="bottom">
	<!-- instructional text speaks in the LABEL voice, not the celebration display font -->
		<BitmapText
			text="PRESS ANYWHERE TO CONTINUE"
			anchor={{ x: 0.5, y: 1 }}
			x={context.stateLayoutDerived.mainLayout().width * 0.5}
			y={context.stateLayoutDerived.mainLayout().height - 18}
			{alpha}
			style={superLabelStyle(26, { align: 'center' })}
		/>
	</MainContainer>
{/if}
<OnHotkey hotkey="Space" onpress={() => press()} />
<OnPressFullScreen onpress={() => press()} />
