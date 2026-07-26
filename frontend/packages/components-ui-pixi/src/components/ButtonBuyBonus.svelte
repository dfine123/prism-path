<script lang="ts">
	import { Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';
	import { stateModal, stateBet, stateBetDerived } from 'state-shared';

	import UiGlass from './UiGlass.svelte';
	import UiGlyph from './UiGlyph.svelte';
	import { getContext } from '../context';
	import { SUPER_UI } from '../theme';

	// Buy Bonus: a rounded-SQUARE gold-star button standing just left of the deck, a bit
	// taller than the bar (the references' detached-but-aligned pattern). A different
	// silhouette on purpose — a purchase, not a control. Active bet-mode -> gold ring;
	// pressing again disarms it (logic unchanged from the template).
	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const { stateXstateDerived, eventEmitter } = getContext();
	const T = SUPER_UI;
	const sizes = $derived(props.sizes ?? { width: T.buy.size, height: T.buy.size });
	const disabled = $derived(!stateXstateDerived.isIdle());
	const active = $derived(stateBetDerived.activeBetMode()?.type === 'activate');

	const openModal = () => (stateModal.modal = { name: 'buyBonus' });
	const disableActiveBetMode = () => (stateBet.activeBetModeKey = 'BASE');
	const onpress = () => {
		eventEmitter.broadcast({ type: 'soundPressGeneral' });

		if (active) {
			disableActiveBetMode();
		} else {
			openModal();
		}
	};
</script>

<Button {...props} {sizes} {disabled} {onpress}>
	{#snippet children({ center, hovered, pressed })}
		<Container {...center} scale={pressed ? T.press : 1} alpha={disabled ? T.dim : 1}>
			<UiGlass
				width={sizes.width}
				height={sizes.height}
				radius={T.buy.r}
				lit={!disabled && hovered}
				accent={active ? T.color.gold : null}
			/>
			<UiGlyph icon="star" shadow size={sizes.width * 0.62} color={T.color.gold} />
		</Container>
	{/snippet}
</Button>
