<script lang="ts">
	import { Sprite, type SpriteProps } from 'pixi-svelte';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';
	import { stateFx } from '../game/stateFx.svelte';
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
	// Trimmed with the win-line beats so the breath never outlasts the (snappier) line.
	const BREATH_MS = 380;
	const BREATH_AMP = 0.065;

	// LAND state = a soft cushion squash (height dips, width gives a touch) so the reel stop
	// reads as absorbed impact, not concrete. oncomplete returns the symbol to 'static'.
	const LAND_MS = 190;
	const LAND_AMP = 0.06;

	let breath = $state(1);
	let squashW = $state(1);
	let squashH = $state(1);

	$effect(() => {
		if (props.state === 'win') {
			let lastT = performance.now();
			let el = 0;
			let raf = 0;
			const frame = () => {
				const t = performance.now();
				el += (t - lastT) * stateFx.winSpeed; // click-to-skip accelerates the breath
				lastT = t;
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
		if (props.state === 'land') {
			const start = performance.now();
			let raf = 0;
			const frame = () => {
				const u = Math.min(1, (performance.now() - start) / LAND_MS);
				// fast dip, relaxed recovery (never a step-change)
				const k = Math.sin(Math.PI * Math.pow(u, 0.6));
				squashH = 1 - LAND_AMP * k;
				squashW = 1 + LAND_AMP * 0.6 * k;
				if (u < 1) {
					raf = requestAnimationFrame(frame);
				} else {
					squashW = 1;
					squashH = 1;
					props.oncomplete?.();
				}
			};
			raf = requestAnimationFrame(frame);
			return () => cancelAnimationFrame(raf);
		}
		breath = 1;
		squashW = 1;
		squashH = 1;
		props.oncomplete?.();
	});
</script>

<Sprite
	x={props.x}
	y={props.y}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * breath * squashW}
	height={SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * breath * squashH}
/>
