<script lang="ts">
	import { Container } from 'pixi-svelte';

	import SymbolSpine from './SymbolSpine.svelte';
	import SymbolSprite from './SymbolSprite.svelte';
	import StickyEyeGlow from './StickyEyeGlow.svelte';
	import WildTrailSymbol from './WildTrailSymbol.svelte';
	import { getSymbolInfo } from '../game/utils';
	import type { SymbolState, RawSymbol } from '../game/types';
	import { getContext } from '../game/context';

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
	// and a STICKY dragon ALWAYS renders as a seated dragon.
	// (Multiplier badges render in the dedicated MultiplierBadges layer, above the ribbons.)
	const isTrailWild = $derived(
		props.rawSymbol.name === 'WILD' &&
			!props.rawSymbol.sticky &&
			!!props.rawSymbol.direction &&
			(props.rawSymbol.multiplier ?? 0) > 1,
	);
</script>

{#if isTrailWild}
	<WildTrailSymbol
		direction={props.rawSymbol.direction as 'up' | 'down' | 'left' | 'right'}
		state={props.state}
		oncomplete={props.oncomplete}
	/>
{:else if isSprite}
	{@const isStickyDragon = props.rawSymbol.name === 'WILD' && !!props.rawSymbol.sticky}
	{@const dormantSeat = isStickyDragon && !!props.rawSymbol.dormant}
	<!-- sticky dragon: the path-gradient streams THROUGH the keyed-out eye sockets
	     (drawn behind the art — the face masks it into crisp crystal-cut eyes).
	     A DORMANT seat (dragon flew this spin) renders invisibly — alpha 0, not removed,
	     so state animations still run and oncomplete still fires for the sequencers —
	     leaving the glowing marker box as the only claim on the square. -->
	{#if isStickyDragon && !dormantSeat}
		<StickyEyeGlow
			x={props.x}
			y={props.y}
			direction={props.rawSymbol.direction as 'up' | 'down' | 'left' | 'right' | undefined}
		/>
	{/if}
	<Container alpha={dormantSeat ? 0 : 1}>
		<SymbolSprite {symbolInfo} state={props.state} x={props.x} y={props.y} oncomplete={props.oncomplete} />
	</Container>
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
