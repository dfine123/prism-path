<script lang="ts">
	import type { Snippet } from 'svelte';

	import { Container, Text } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';

	import UiGlass from './UiGlass.svelte';
	import UiGlyph from './UiGlyph.svelte';
	import type { ButtonIcon } from '../types';
	import { i18nDerived } from '../i18n/i18nDerived';
	import { SUPER_UI } from '../theme';

	// Standard Crystal Console control: circular glass face + vector glyph + small caps
	// label. States per the system language: hover rim-light, press shrink, active gold
	// ring, disabled dim. Same component everywhere a circular control appears.
	type Props = Omit<ButtonProps, 'children'> & {
		icon: ButtonIcon;
		sizes: { width: number; height: number };
		active?: boolean;
		showLabel?: boolean; // steppers go icon-only
		variant?: 'dark' | 'light'; // legacy prop, accepted for API compat
		children?: Snippet;
	};

	const {
		icon,
		active,
		showLabel = true,
		variant = 'dark',
		children: childrenFromParent,
		...buttonProps
	}: Props = $props();

	const T = SUPER_UI;
	const d = $derived(Math.min(buttonProps.sizes.width, buttonProps.sizes.height));
</script>

<Button {...buttonProps}>
	{#snippet children({ center, hovered, pressed })}
		<Container {...center} scale={pressed ? T.press : 1} alpha={buttonProps.disabled ? T.dim : 1}>
			<UiGlass
				width={d}
				height={d}
				radius={d / 2}
				lit={!buttonProps.disabled && hovered}
				accent={active ? T.color.gold : null}
			/>
			<UiGlyph
				{icon}
				shadow
				y={showLabel ? -d * 0.09 : 0}
				size={d * (showLabel ? 0.42 : 0.46)}
				color={active ? T.color.gold : T.color.text}
			/>
			{#if showLabel}
				<Text
					anchor={0.5}
					y={d * 0.26}
					text={i18nDerived[icon]()}
					style={{
						align: 'center',
						fontFamily: T.font,
						fontWeight: '600',
						fontSize: T.fs.btnLabel,
						fill: active ? T.color.gold : T.color.textDim,
					}}
				/>
			{/if}
			{@render childrenFromParent?.()}
		</Container>
	{/snippet}
</Button>
