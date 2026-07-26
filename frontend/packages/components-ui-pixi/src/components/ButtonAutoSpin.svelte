<script lang="ts">
	import { Container } from 'pixi-svelte';
	import type { ButtonProps } from 'components-pixi';
	import { stateBet, stateBetDerived, stateModal } from 'state-shared';

	import UiButton from './UiButton.svelte';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';
	import ButtonBetAutoSpinsCounter from './ButtonBetAutoSpinsCounter.svelte';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const context = getContext();
	const sizes = $derived(props.sizes ?? { width: SUPER_UI.btn, height: SUPER_UI.btn });
	const active = $derived(stateBetDerived.hasAutoBetCounter());
	const disabled = $derived.by(() => {
		if (stateBet.isSpaceHold) return true;
		if (!context.stateXstateDerived.isIdle() && !stateBetDerived.hasAutoBetCounter()) return true;
		// the cost check only gates ARMING autoplay — while a run is active this button
		// means STOP AUTOPLAY and must stay live even when the balance dips below cost
		if (!stateBetDerived.hasAutoBetCounter() && !stateBetDerived.isBetCostAvailable()) return true;
		return false;
	});

	const stopAutoSpin = () => (stateBet.autoSpinsCounter = 0);
	const openModal = () => (stateModal.modal = { name: 'autoSpin' });
	const onpress = () => {
		context.eventEmitter.broadcast({ type: 'soundPressGeneral' });
		stateBetDerived.hasAutoBetCounter() ? stopAutoSpin() : openModal();
	};
</script>

<UiButton {...props} {sizes} {active} {onpress} {disabled} icon="autoSpin">
	<Container x={sizes.width * 0.5} y={sizes.height * 0.5} scale={sizes.width / 150}>
		<ButtonBetAutoSpinsCounter />
	</Container>
</UiButton>
