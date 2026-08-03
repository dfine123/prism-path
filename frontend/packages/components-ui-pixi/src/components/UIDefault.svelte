<script lang="ts">
	import type { Snippet } from 'svelte';

	import { getContextLayout } from 'utils-layout';
	import { EnableSpaceHold } from 'components-shared';
	import { stateModal, stateUi, stateBetDerived } from 'state-shared';
	import { getContext } from '../context';

	import UiFadeContainer from './UiFadeContainer.svelte';
	import LayoutDesktop from './LayoutDesktop.svelte';
	import LayoutPortrait from './LayoutPortrait.svelte';
	import LayoutLandscape from './LayoutLandscape.svelte';
	import LayoutTablet from './LayoutTablet.svelte';
	import LabelBalance from './LabelBalance.svelte';
	import LabelWin from './LabelWin.svelte';
	import LabelBet from './LabelBet.svelte';
	import ButtonPayTable from './ButtonPayTable.svelte';
	import ButtonGameRules from './ButtonGameRules.svelte';
	import ButtonSettings from './ButtonSettings.svelte';
	import ButtonBuyBonus from './ButtonBuyBonus.svelte';
	import ButtonBet from './ButtonBet.svelte';
	import ButtonTurbo from './ButtonTurbo.svelte';
	import ButtonAutoSpin from './ButtonAutoSpin.svelte';
	import ButtonIncrease from './ButtonIncrease.svelte';
	import ButtonDecrease from './ButtonDecrease.svelte';
	import ButtonMenu from './ButtonMenu.svelte';
	import ButtonMenuClose from './ButtonMenuClose.svelte';
	import ButtonSoundSwitch from './ButtonSoundSwitch.svelte';

	type Props = {
		gameName: Snippet;
		logo: Snippet;
	};

	const props: Props = $props();

	const { stateLayoutDerived } = getContextLayout();
	const context = getContext();

	const LAYOUT_COMPONENT_MAP = {
		desktop: LayoutDesktop,
		portrait: LayoutPortrait,
		landscape: LayoutLandscape,
		tablet: LayoutTablet,
	};

	const LayoutComponent = $derived(LAYOUT_COMPONENT_MAP[stateLayoutDerived.layoutType()]);
</script>

<!-- the rebet loop may only be ARMED from true idle at the keydown that starts the hold;
     mid-round holds still force turbo. Overlay + autoplay guards mirror the console's own
     press gate: a hold begun behind a modal (press blocked, machine idle) must not arm a
     loop that later nests inside an autoplay run and bypasses its loss/win limits. -->
<EnableSpaceHold
	canArm={() =>
		stateModal.modal === null &&
		!stateUi.menuOpen &&
		!stateUi.pressCatcherActive &&
		!stateBetDerived.hasAutoBetCounter() &&
		context.stateXstateDerived.isIdle()}
/>

<UiFadeContainer>
	<LayoutComponent>
		{#snippet gameName()}
			{@render props.gameName()}
		{/snippet}

		{#snippet logo()}
			{@render props.logo()}
		{/snippet}

		{#snippet amountBalance(labelProps)}
			<LabelBalance {...labelProps} />
		{/snippet}

		{#snippet amountWin(labelProps)}
			<LabelWin {...labelProps} />
		{/snippet}

		{#snippet amountBet(labelProps)}
			<LabelBet {...labelProps} />
		{/snippet}

		{#snippet buttonBuyBonus(buttonProps)}
			<ButtonBuyBonus {...buttonProps} />
		{/snippet}

		{#snippet buttonBet(buttonProps)}
			<ButtonBet {...buttonProps} />
		{/snippet}

		{#snippet buttonTurbo(buttonProps)}
			<ButtonTurbo {...buttonProps} />
		{/snippet}

		{#snippet buttonAutoSpin(buttonProps)}
			<ButtonAutoSpin {...buttonProps} />
		{/snippet}

		{#snippet buttonIncrease(buttonProps)}
			<ButtonIncrease {...buttonProps} />
		{/snippet}

		{#snippet buttonDecrease(buttonProps)}
			<ButtonDecrease {...buttonProps} />
		{/snippet}

		{#snippet buttonMenu(buttonProps)}
			<ButtonMenu {...buttonProps} />
		{/snippet}

		{#snippet buttonMenuClose(buttonProps)}
			<ButtonMenuClose {...buttonProps} />
		{/snippet}

		{#snippet buttonPayTable(buttonProps)}
			<ButtonPayTable {...buttonProps} />
		{/snippet}

		{#snippet buttonGameRules(buttonProps)}
			<ButtonGameRules {...buttonProps} />
		{/snippet}

		{#snippet buttonSettings(buttonProps)}
			<ButtonSettings {...buttonProps} />
		{/snippet}

		{#snippet buttonSoundSwitch(buttonProps)}
			<ButtonSoundSwitch {...buttonProps} />
		{/snippet}
	</LayoutComponent>
</UiFadeContainer>
