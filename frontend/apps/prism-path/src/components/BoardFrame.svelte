<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<script lang="ts">
	import { Graphics, Sprite, SpineProvider, SpineTrack } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, SYMBOL_SIZE } from '../game/constants';

	const context = getContext();
	const SPINE_SCALE = { width: 0.62, height: 0.66 };
	const SPRITE_SCALE = { width: 1.14, height: 1.15 };
	const POSITION_ADJUSTMENT = 1.01;

	type AnimationName = 'reelhouse_glow_start' | 'reelhouse_glow_idle' | 'reelhouse_glow_exit';

	let animationName = $state<AnimationName | undefined>(undefined);
	let loop = $state(false);

	context.eventEmitter.subscribeOnMount({
		boardFrameGlowShow: () => {
			animationName = 'reelhouse_glow_start';
			loop = false;
		},
		boardFrameGlowHide: () => {
			if (animationName) animationName = 'reelhouse_glow_exit';
		},
	});
</script>

{#if animationName}
	<SpineProvider
		zIndex={-1}
		key="reelhouse"
		x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
		y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
		width={context.stateGameDerived.boardLayout().width * SPINE_SCALE.width}
		height={context.stateGameDerived.boardLayout().height * SPINE_SCALE.height}
	>
		<SpineTrack
			trackIndex={0}
			{animationName}
			{loop}
			listener={{
				complete: (entry) => {
					if (entry.animation) {
						if (entry.animation.name === 'reelhouse_glow_start') {
							animationName = 'reelhouse_glow_idle';
							loop = true;
						}

						if (entry.animation.name === 'reelhouse_glow_exit') {
							animationName = undefined;
							loop = false;
						}
					}
				},
			}}
		/>
	</SpineProvider>
{/if}

<!-- Board backing: mid-dark grey panel + light gridlines aligned to the 5x5 cells -->
<Graphics
	x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
	y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
	draw={(g) => {
		const PW = BOARD_SIZES.width * SPRITE_SCALE.width;
		const PH = BOARD_SIZES.height * SPRITE_SCALE.height;
		g.roundRect(-PW / 2, -PH / 2, PW, PH, 22).fill({ color: 0x2c2c34 });
		const W = BOARD_SIZES.width;
		const H = BOARD_SIZES.height;
		for (let i = 0; i <= 5; i++) {
			const gx = -W / 2 + i * SYMBOL_SIZE;
			g.moveTo(gx, -H / 2).lineTo(gx, H / 2);
			const gy = -H / 2 + i * SYMBOL_SIZE;
			g.moveTo(-W / 2, gy).lineTo(W / 2, gy);
		}
		g.stroke({ width: 2, color: 0x6f6f7e, alpha: 0.5 });
	}}
/>

<Sprite
	key="prismFrameEdge"
	anchor={0.5}
	x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
	y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
	width={context.stateGameDerived.boardLayout().width * SPRITE_SCALE.width}
	height={context.stateGameDerived.boardLayout().height * SPRITE_SCALE.height}
/>
