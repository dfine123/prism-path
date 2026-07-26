<script lang="ts">
	import type { ButtonProps } from 'components-pixi';
	import { stateBet, stateBetDerived, stateConfig } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const sizes = $derived(props.sizes ?? { width: SUPER_UI.btnSm, height: SUPER_UI.btnSm });
	const nextBigger = $derived(
		[...stateConfig.betAmountOptions].sort((a, b) => a - b).find((o) => o > stateBet.betAmount),
	);
	// enabled ONLY when pressing would actually change the bet: setBetAmount clamps to
	// balance/costMultiplier, so with a clamped off-options bet the raw `=== biggest`
	// check left a live-looking button whose presses were silently swallowed
	const costMult = $derived.by(() => {
		const mode = stateBetDerived.activeBetMode();
		return mode?.type === 'activate' ? mode.costMultiplier : 1;
	});
	const disabled = $derived.by(() => {
		if (!context.stateXstateDerived.isIdle()) return true;
		if (nextBigger === undefined) return true;
		return Math.min(nextBigger, stateBet.balanceAmount / costMult) <= stateBet.betAmount;
	});

	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		if (nextBigger !== undefined) stateBetDerived.setBetAmount(nextBigger);
	};
</script>

<UiButton {...props} {sizes} showLabel={false} {onpress} {disabled} icon="increase" />
