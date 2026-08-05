<script lang="ts">
	import { Popup } from 'components-shared';
	import { zIndex } from 'constants-shared/zIndex';
	import { getContextLayout } from 'utils-layout';
	import { stateModal, stateMetaDerived } from 'state-shared';

	import BonusCards from './BonusCards.svelte';
	import BetMenuAmountToggle from './BetMenuAmountToggle.svelte';
	import BonusContentWrapLarge from './BonusContentWrapLarge.svelte';
	import BonusContentWrapPortrait from './BonusContentWrapPortrait.svelte';
	import BonusContentWrapLandscape from './BonusContentWrapLandscape.svelte';

	const { stateLayoutDerived } = getContextLayout();

	const activateList = $derived(
		stateMetaDerived.betModeMetaList().filter((item) => item.type === 'activate'),
	);

	const buyList = $derived(
		stateMetaDerived.betModeMetaList().filter((item) => item.type === 'buy'),
	);

	const COMPONENT_MAP = {
		desktop: BonusContentWrapLarge,
		tablet: BonusContentWrapLarge,
		portrait: BonusContentWrapPortrait,
		landscape: BonusContentWrapLandscape,
	} as const;

	const BonusContentWrap = $derived(COMPONENT_MAP[stateLayoutDerived.layoutType()]);

	// portrait flows normally so the close key can perch on the content; the large and
	// landscape wraps position their content absolutely (no flow size), so the close
	// key falls back to the viewport corner there
	const closeAnchor = $derived(
		stateLayoutDerived.layoutType() === 'portrait' ? ('content' as const) : ('viewport' as const),
	);
</script>

{#if stateModal.modal?.name === 'buyBonus'}
	<Popup zIndex={zIndex.modal} {closeAnchor} onclose={() => (stateModal.modal = null)}>
		<BonusContentWrap maxListLength={Math.max(activateList.length, buyList.length)}>
			{#snippet betAmount()}
				<BetMenuAmountToggle />
			{/snippet}

			{#snippet bonusCardsActivate()}
				<BonusCards list={activateList} />
			{/snippet}

			{#snippet bonusCardsBuy()}
				<BonusCards list={buyList} />
			{/snippet}
		</BonusContentWrap>
	</Popup>
{/if}
