<script lang="ts">
	import { Tween } from 'svelte/motion';

	import { stateBet } from 'state-shared';
	import { numberToCurrencyString } from 'utils-shared/amount';

	import UiLabel from './UiLabel.svelte';
	import { i18nDerived } from '../i18n/i18nDerived';

	type Props = {
		stacked?: boolean;
		width?: number;
		bare?: boolean;
	};

	const props: Props = $props();
	// money glides with a decelerating roll (expo-out), not the default linear crawl
	const expoOut = (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));
	const balanceTween = new Tween(stateBet.balanceAmount, { duration: 350, easing: expoOut });
	const label = $derived(i18nDerived.balance());
	const value = $derived(numberToCurrencyString(balanceTween.current));

	$effect(() => {
		balanceTween.set(stateBet.balanceAmount);
	});
</script>

<UiLabel tiled {label} {value} stacked={props.stacked} width={props.width} bare={props.bare} />
