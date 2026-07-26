<script lang="ts">
	import { Tween } from 'svelte/motion';

	import { stateBet } from 'state-shared';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import UiLabel from './UiLabel.svelte';
	import { i18nDerived } from '../i18n/i18nDerived';
	import { SUPER_UI } from '../theme';

	type Props = {
		stacked?: boolean;
		width?: number;
		bare?: boolean;
	};

	const props: Props = $props();
	const winBookEventAmountTween = new Tween(stateBet.winBookEventAmount);
	const label = $derived(i18nDerived.win());
	const value = $derived(bookEventAmountToCurrencyString(winBookEventAmountTween.current));
	// the win readout goes gold while a win is on the meter — the console's one live accent
	const accent = $derived(stateBet.winBookEventAmount > 0 ? SUPER_UI.color.gold : null);

	$effect(() => {
		winBookEventAmountTween.set(stateBet.winBookEventAmount);
	});
</script>

<UiLabel tiled {label} {value} stacked={props.stacked} width={props.width} bare={props.bare} {accent} />
