<script lang="ts">
	import { MainContainer, OnPressFullScreen } from 'components-layout';
	import { OnHotkey } from 'components-shared';
	import { BitmapText } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { prismStyle } from '../game/fonts';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import { onMount } from 'svelte';

	type Props = {
		onpress: () => void;
	};

	const props: Props = $props();
	const context = getContext();

	onMount(() => {
		acquireTrailClock();
		return releaseTrailClock;
	});

	// gentle invite breathe (the screen is never dead)
	const alpha = $derived(0.62 + 0.38 * (Math.sin(trailClock.t * Math.PI * 1.3) + 1) * 0.5);
</script>

<MainContainer alignVertical="bottom">
	<BitmapText
		text="PRESS ANYWHERE TO CONTINUE"
		anchor={{ x: 0.5, y: 1 }}
		x={context.stateLayoutDerived.mainLayout().width * 0.5}
		y={context.stateLayoutDerived.mainLayout().height - 18}
		{alpha}
		style={prismStyle(34, { align: 'center' })}
	/>
</MainContainer>
<OnHotkey hotkey="Space" onpress={() => props.onpress()} />
<OnPressFullScreen onpress={() => props.onpress()} />
