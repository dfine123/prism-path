<script lang="ts">
	import type { Snippet } from 'svelte';

	import ModalError from './ModalError.svelte';
	import ModalBetMenu from './ModalBetMenu.svelte';
	import ModalBuyBonus from './ModalBuyBonus.svelte';
	import ModalBuyBonusConfirm from './ModalBuyBonusConfirm.svelte';
	import ModalAutoSpin from './ModalAutoSpin.svelte';
	import ModalAutoSpinMessage from './ModalAutoSpinMessage.svelte';
	import ModalPayTable from './ModalPayTable.svelte';
	import ModalGameRules from './ModalGameRules.svelte';
	import ModalSettings from './ModalSettings.svelte';

	type Props = {
		version: Snippet;
		payTable?: Snippet;
		gameRules?: Snippet;
	};

	const props: Props = $props();
</script>

<ModalError />
<ModalBetMenu />
<ModalBuyBonus />
<ModalBuyBonusConfirm />
<ModalAutoSpin />
<ModalAutoSpinMessage />
<ModalPayTable>
	{#if props.payTable}
		{@render props.payTable()}
	{/if}
	{@render props.version()}
</ModalPayTable>
<ModalGameRules>
	{#if props.gameRules}
		{@render props.gameRules()}
	{/if}
	{@render props.version()}
</ModalGameRules>
<ModalSettings />

<style lang="scss">
	// Deliberate responsive type scale. The template's 50%-root hack halved every rem
	// on phones (6-8px body text, 16px tap rows — audit HIGH). Phones get a modestly
	// smaller root so modal chrome fits, never below legibility (14px root => body
	// text ~12-13px, tap rows >= 40px).
	:global(html) {
		font-size: 16px;
		@media screen and (max-width: 500px) {
			font-size: 87.5%; // 14px
		}
	}
</style>
