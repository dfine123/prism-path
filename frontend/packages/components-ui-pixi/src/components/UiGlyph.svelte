<script lang="ts">
	import { Graphics } from 'pixi-svelte';

	import UiGlyphSelf from './UiGlyph.svelte';
	import { SUPER_UI } from '../theme';
	import { drawGlyph, type GlyphName } from '../glyphs';

	// Thin renderer over the shared glyph geometry (../glyphs.ts). Keeping the drawing in a
	// pure function lets the exact shipped shapes be rendered offscreen and inspected.
	// `size` is the glyph's bounding square; strokes scale with it.
	type Props = {
		x?: number;
		y?: number;
		icon: GlyphName;
		size: number;
		color?: number;
		alpha?: number;
		shadow?: boolean; // soft drop copy under the glyph (domed-key depth)
	};

	const props: Props = $props();
	const col = $derived(props.color ?? SUPER_UI.color.text);
</script>

{#if props.shadow}
	<UiGlyphSelf
		x={props.x}
		y={(props.y ?? 0) + Math.max(1.5, props.size * 0.045)}
		icon={props.icon}
		size={props.size}
		color={0x080510}
		alpha={(props.alpha ?? 1) * 0.45}
	/>
{/if}

<Graphics
	x={props.x ?? 0}
	y={props.y ?? 0}
	alpha={props.alpha ?? 1}
	draw={(g) => drawGlyph(g, { icon: props.icon, size: props.size, color: col })}
/>
