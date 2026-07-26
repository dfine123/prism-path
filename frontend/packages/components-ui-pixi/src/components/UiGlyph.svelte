<script lang="ts">
	import { Graphics } from 'pixi-svelte';

	import UiGlyphSelf from './UiGlyph.svelte';
	import { SUPER_UI } from '../theme';
	import type { ButtonIcon } from '../types';

	// Code-drawn vector glyphs for every control — crisp at any scale, i18n-proof.
	// `size` is the glyph's bounding square; strokes scale with it.
	type Props = {
		x?: number;
		y?: number;
		icon: ButtonIcon | 'spin' | 'stop' | 'star';
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
	draw={(g) => {
		const s = props.size;
		const lw = Math.max(3, s * 0.13);
		const stroke = { width: lw, color: col, cap: 'round' as const, join: 'round' as const };
		switch (props.icon) {
			case 'decrease':
				g.moveTo(-s * 0.38, 0).lineTo(s * 0.38, 0).stroke(stroke);
				break;
			case 'increase':
				g.moveTo(-s * 0.38, 0).lineTo(s * 0.38, 0).stroke(stroke);
				g.moveTo(0, -s * 0.38).lineTo(0, s * 0.38).stroke(stroke);
				break;
			case 'menu':
				for (const dy of [-0.3, 0, 0.3]) {
					g.moveTo(-s * 0.36, s * dy).lineTo(s * 0.36, s * dy).stroke(stroke);
				}
				break;
			case 'menuExit':
				g.moveTo(-s * 0.32, -s * 0.32).lineTo(s * 0.32, s * 0.32).stroke(stroke);
				g.moveTo(-s * 0.32, s * 0.32).lineTo(s * 0.32, -s * 0.32).stroke(stroke);
				break;
			case 'turbo':
				// double chevron — speed
				for (const dx of [-0.22, 0.14]) {
					g.moveTo(s * (dx - 0.14), -s * 0.32)
						.lineTo(s * (dx + 0.18), 0)
						.lineTo(s * (dx - 0.14), s * 0.32)
						.stroke(stroke);
				}
				break;
			case 'autoSpin':
			case 'spin': {
				// circular arrow: open arc + arrowhead at its leading end
				const r = s * 0.34;
				const a0 = -Math.PI * 0.35;
				const a1 = Math.PI * 1.05;
				g.arc(0, 0, r, a0, a1).stroke(stroke);
				const hx = Math.cos(a0) * r;
				const hy = Math.sin(a0) * r;
				const ah = s * 0.2;
				g.poly([
					{ x: hx + ah * 0.7, y: hy - ah * 0.28 },
					{ x: hx - ah * 0.42, y: hy - ah * 0.6 },
					{ x: hx + ah * 0.05, y: hy + ah * 0.52 },
				]).fill({ color: col });
				break;
			}
			case 'stop':
				g.roundRect(-s * 0.28, -s * 0.28, s * 0.56, s * 0.56, s * 0.1).fill({ color: col });
				break;
			case 'star': {
				// fat friendly 5-point star + a tiny glint
				const R = s * 0.46;
				const rIn = R * 0.5;
				const pts: { x: number; y: number }[] = [];
				for (let i = 0; i < 10; i++) {
					const a = -Math.PI / 2 + (i * Math.PI) / 5;
					const rad = i % 2 === 0 ? R : rIn;
					pts.push({ x: Math.cos(a) * rad, y: Math.sin(a) * rad });
				}
				g.poly(pts).fill({ color: col });
				g.poly(pts).stroke({ width: Math.max(2, s * 0.05), color: col, join: 'round' });
				g.circle(-R * 0.22, -R * 0.3, Math.max(1.6, s * 0.05)).fill({ color: 0xffffff, alpha: 0.85 });
				break;
			}
			case 'payTable': {
				// stacked coins
				for (const [dy, rw] of [
					[0.22, 0.34],
					[0.02, 0.34],
					[-0.18, 0.34],
				] as const) {
					g.ellipse(0, s * dy, s * rw, s * 0.13).stroke(stroke);
				}
				break;
			}
			case 'info':
				g.circle(0, -s * 0.3, lw * 0.62).fill({ color: col });
				g.moveTo(0, -s * 0.08).lineTo(0, s * 0.34).stroke(stroke);
				break;
			case 'settings': {
				// gear: ring + teeth + hub
				const r = s * 0.26;
				g.circle(0, 0, r).stroke(stroke);
				for (let i = 0; i < 6; i++) {
					const a = (i / 6) * Math.PI * 2;
					g.moveTo(Math.cos(a) * (r + lw * 0.2), Math.sin(a) * (r + lw * 0.2))
						.lineTo(Math.cos(a) * (r + lw * 1.15), Math.sin(a) * (r + lw * 1.15))
						.stroke(stroke);
				}
				g.circle(0, 0, r * 0.32).fill({ color: col });
				break;
			}
			case 'soundOn':
			case 'soundOff': {
				// speaker
				g.poly([
					{ x: -s * 0.38, y: -s * 0.14 },
					{ x: -s * 0.16, y: -s * 0.14 },
					{ x: s * 0.05, y: -s * 0.32 },
					{ x: s * 0.05, y: s * 0.32 },
					{ x: -s * 0.16, y: s * 0.14 },
					{ x: -s * 0.38, y: s * 0.14 },
				]).fill({ color: col });
				if (props.icon === 'soundOn') {
					g.arc(s * 0.1, 0, s * 0.2, -Math.PI * 0.35, Math.PI * 0.35).stroke(stroke);
					g.arc(s * 0.1, 0, s * 0.33, -Math.PI * 0.32, Math.PI * 0.32).stroke(stroke);
				} else {
					g.moveTo(s * 0.16, -s * 0.16).lineTo(s * 0.42, s * 0.16).stroke(stroke);
					g.moveTo(s * 0.16, s * 0.16).lineTo(s * 0.42, -s * 0.16).stroke(stroke);
				}
				break;
			}
		}
	}}
/>
