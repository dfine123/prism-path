<script lang="ts">
	import SymbolSpine from './SymbolSpine.svelte';
	import SymbolSprite from './SymbolSprite.svelte';
	import WildTrailSymbol from './WildTrailSymbol.svelte';
	import { getSymbolInfo } from '../game/utils';
	import type { SymbolState, RawSymbol } from '../game/types';
	import { getContext } from '../game/context';
	import { prismStyle } from '../game/fonts';
	import { SYMBOL_SIZE } from '../game/constants';
	import { EASE } from '../game/motion';
	import { BitmapText, Container } from 'pixi-svelte';

	type Props = {
		x?: number;
		y?: number;
		state: SymbolState;
		rawSymbol: RawSymbol;
		oncomplete?: () => void;
		loop?: boolean;
	};

	const props: Props = $props();
	const context = getContext();
	const symbolInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: props.state }));
	const isSprite = $derived(symbolInfo.type === 'sprite');
	// A beast-created wild (has a multiplier) renders as the ANIMATED PRISM TRAIL, not a dragon.
	// A freshly-landed beast (direction but no multiplier yet) stays a dragon until it fires,
	// and a STICKY dragon ALWAYS renders as a seated dragon (with its multiplier badge).
	const isTrailWild = $derived(
		props.rawSymbol.name === 'WILD' &&
			!props.rawSymbol.sticky &&
			!!props.rawSymbol.direction &&
			(props.rawSymbol.multiplier ?? 0) > 1,
	);

	// multiplier badge: clean subtle pop-in whenever the value appears or grows (overlap x2->x6)
	let badgeScale = $state(1);
	let badgeAlpha = $state(1);
	$effect(() => {
		const m = props.rawSymbol.multiplier;
		if (!m) return;
		let lastT = performance.now();
		let el = 0;
		let raf = 0;
		const POP_MS = 240;
		const frame = () => {
			const t = performance.now();
			el += t - lastT;
			lastT = t;
			const u = Math.min(1, el / POP_MS);
			badgeScale = 0.7 + 0.3 * EASE.impact(u);
			badgeAlpha = Math.min(1, u * 3);
			if (u < 1) raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});
</script>

{#if isTrailWild}
	<WildTrailSymbol
		direction={props.rawSymbol.direction as 'up' | 'down' | 'left' | 'right'}
		state={props.state}
		oncomplete={props.oncomplete}
	/>
{:else if isSprite}
	<SymbolSprite {symbolInfo} state={props.state} x={props.x} y={props.y} oncomplete={props.oncomplete} />
{:else}
	<SymbolSpine
		loop={props.loop}
		{symbolInfo}
		x={props.x}
		y={props.y}
		showWinFrame={props.state === 'win' && !['S', 'M'].includes(props.rawSymbol.name)}
		listener={{
			complete: props.oncomplete,
			event: (_, event) => {
				if (event.data?.name === 'wildExplode') {
					context.eventEmitter?.broadcast({ type: 'soundOnce', name: 'sfx_wild_explode' });
				}
			},
		}}
	/>
{/if}

{#if props.rawSymbol.multiplier}
	{@const sticky = !!props.rawSymbol.sticky}
	<!-- a STICKY dragon's badge sits by its path edge (bottom of the cell), never covering
	     the seated dragon; trail cells keep the centred badge -->
	<Container
		x={props.x ?? 0}
		y={(props.y ?? 0) + (sticky ? SYMBOL_SIZE * 0.31 : 0)}
		scale={badgeScale}
		alpha={badgeAlpha}
	>
		<BitmapText
			anchor={0.5}
			text={`${props.rawSymbol.multiplier}X`}
			style={prismStyle(sticky ? 34 : 50)}
		/>
	</Container>
{/if}
