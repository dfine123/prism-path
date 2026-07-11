<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<script lang="ts">
	import { Graphics, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, SYMBOL_SIZE } from '../game/constants';
	import { paletteAt } from '../game/motion';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';
	import { stateDev, FRAME_OPTIONS } from '../game/stateDev.svelte';

	const context = getContext();
	// frame candidate + fit come from the DEV picker (DevFramePanel) until a frame is locked
	const SPRITE_SCALE = $derived({ width: stateDev.scaleW, height: stateDev.scaleH });
	const frameKey = $derived(FRAME_OPTIONS[stateDev.frameIndex].key);
	// frame/grid sit EXACTLY on the board centre — the symbols' lattice and the drawn grid
	// must share one origin (was *1.01, a template fudge shifting the grid ~7px off-lattice)
	const POSITION_ADJUSTMENT = 1;

	// FREE-GAME frame glow — code-drawn animated prism halo around the whole board
	// (replaces the template "reelhouse" spine).
	let glowActive = $state(false);

	$effect(() => {
		if (glowActive) {
			acquireTrailClock();
			return releaseTrailClock;
		}
	});

	context.eventEmitter.subscribeOnMount({
		boardFrameGlowShow: () => (glowActive = true),
		boardFrameGlowHide: () => (glowActive = false),
	});
</script>

{#if glowActive}
	<Graphics
		blendMode="add"
		zIndex={-1}
		draw={(g) => {
			const t = trailClock.t;
			const bl = context.stateGameDerived.boardLayout();
			const cx = bl.x * POSITION_ADJUSTMENT;
			const cy = bl.y * POSITION_ADJUSTMENT;
			const w = bl.width * SPRITE_SCALE.width + 26;
			const h = bl.height * SPRITE_SCALE.height + 26;
			const breathe = 0.7 + 0.3 * Math.sin(t * Math.PI * 1.1);
			// layered halo: wide soft bloom -> mid -> tight hue ring (hues slowly cycling)
			g.roundRect(cx - w / 2 - 16, cy - h / 2 - 16, w + 32, h + 32, 34).stroke({
				width: 30,
				color: paletteAt(t * 0.16),
				alpha: 0.08 * breathe,
			});
			g.roundRect(cx - w / 2 - 6, cy - h / 2 - 6, w + 12, h + 12, 28).stroke({
				width: 12,
				color: paletteAt(t * 0.16 + 0.12),
				alpha: 0.16 * breathe,
			});
			g.roundRect(cx - w / 2, cy - h / 2, w, h, 24).stroke({
				width: 4,
				color: paletteAt(t * 0.16 + 0.24),
				alpha: 0.5 * breathe,
			});
		}}
	/>
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
	key={frameKey}
	anchor={0.5}
	x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT}
	y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT}
	width={context.stateGameDerived.boardLayout().width * SPRITE_SCALE.width}
	height={context.stateGameDerived.boardLayout().height * SPRITE_SCALE.height}
/>
