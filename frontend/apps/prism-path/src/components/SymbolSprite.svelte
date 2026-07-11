<script lang="ts">
	import { Sprite, type SpriteProps } from 'pixi-svelte';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import type { SymbolState } from '../game/types';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
		state?: SymbolState;
		oncomplete?: () => void;
	};

	const props: Props = $props();

	// WIN state = a subtle two-pulse breath (anticipation of the line light passing through);
	// oncomplete fires when the breath settles, which is what paces the win-line sequence.
	const BREATH_MS = 780;
	const BREATH_AMP = 0.065;

	let breath = $state(1);

	$effect(() => {
		if (props.state === 'win') {
			const start = performance.now();
			let raf = 0;
			const frame = () => {
				const el = performance.now() - start;
				const u = Math.min(1, el / BREATH_MS);
				// two soft sine pulses that relax back to rest
				breath = 1 + BREATH_AMP * Math.sin(u * Math.PI * 2) * Math.sin(u * Math.PI);
				if (u < 1) {
					raf = requestAnimationFrame(frame);
				} else {
					breath = 1;
					props.oncomplete?.();
				}
			};
			raf = requestAnimationFrame(frame);
			return () => cancelAnimationFrame(raf);
		}
		breath = 1;
		props.oncomplete?.();
	});
</script>

<Sprite
	x={props.x}
	y={props.y}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * breath}
	height={SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * breath}
/>
