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
	// money glides with a decelerating roll (expo-out), not the default linear crawl
	const expoOut = (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));
	const winBookEventAmountTween = new Tween(stateBet.winBookEventAmount, { duration: 350, easing: expoOut });
	const label = $derived(i18nDerived.win());
	const value = $derived(bookEventAmountToCurrencyString(winBookEventAmountTween.current));
	// the win readout goes gold while a win is on the meter — the console's one live
	// accent. Keyed off the TWEENED value that is actually displayed, so the gold holds
	// while the old amount visibly drains instead of snapping grey on the next spin.
	const accent = $derived(winBookEventAmountTween.current > 0 ? SUPER_UI.color.gold : null);

	$effect(() => {
		winBookEventAmountTween.set(stateBet.winBookEventAmount);
	});
</script>

<UiLabel tiled {label} {value} stacked={props.stacked} width={props.width} bare={props.bare} {accent} />
