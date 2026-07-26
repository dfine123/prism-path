<script lang="ts">
	import { Text } from 'pixi-svelte';

	import UiGlass from './UiGlass.svelte';
	import { SUPER_UI } from '../theme';

	// Money-truth readout: small caps dim label over a bright value. Two modes:
	//  - capsule (default): its own glass, centred on the origin — portrait floaters
	//  - bare: text only, LEFT-aligned from the origin — lives inside the console bar
	// Display-only look by design — a readout must never read as a button.
	type Props = {
		label: string;
		value: string;
		tiled?: boolean; // legacy prop, accepted for API compat
		stacked?: boolean;
		width?: number; // block width (value shrinks to stay inside)
		accent?: number | null; // e.g. gold while a win is showing
		bare?: boolean;
	};

	const props: Props = $props();
	const T = SUPER_UI;

	const w = $derived(props.width ?? T.caps.w);
	// long values shrink to stay inside the block instead of overflowing it
	const valueFs = $derived.by(() => {
		const base = props.bare ? T.fs.barValue : T.fs.value;
		const budget = (w - (props.bare ? 6 : 36)) / (base * 0.56); // ~avg glyph width, UI font
		return base * Math.min(1, budget / Math.max(props.value.length, 1));
	});
</script>

{#if props.bare}
	<!-- recessed instrument well: the readout sinks INTO the deck behind glass -->
	<UiGlass width={w} height={76} radius={18} tone="inset" accent={props.accent ?? null} />
	<Text
		anchor={0.5}
		y={-19}
		text={props.label.toUpperCase()}
		style={{ fontFamily: T.font, fontWeight: '600', fontSize: T.fs.barLabel, fill: T.color.textDim }}
	/>
	<Text
		anchor={0.5}
		y={12}
		text={props.value}
		style={{
			fontFamily: T.font,
			fontWeight: '700',
			fontSize: valueFs,
			fill: props.accent ?? T.color.text,
		}}
	/>
{:else}
	<UiGlass width={w} height={T.caps.h} radius={T.caps.r} accent={props.accent ?? null} />
	<Text
		anchor={0.5}
		y={-T.caps.h / 2 + 26}
		text={props.label.toUpperCase()}
		style={{ fontFamily: T.font, fontWeight: '600', fontSize: T.fs.capsLabel, fill: T.color.textDim }}
	/>
	<Text
		anchor={0.5}
		y={11}
		text={props.value}
		style={{
			fontFamily: T.font,
			fontWeight: '700',
			fontSize: valueFs,
			fill: props.accent ?? T.color.text,
		}}
	/>
{/if}
