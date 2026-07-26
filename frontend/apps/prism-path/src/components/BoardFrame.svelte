<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<script lang="ts">
	import { Container, Graphics, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { paletteAt } from '../game/motion';
	import { stateFx } from '../game/stateFx.svelte';
	import { trailClock, acquireTrailClock, releaseTrailClock } from '../game/trailClock.svelte';

	const context = getContext();
	// LOCKED frame: crystal v2 (board1, LANDSCAPE — the board conforms to its opening aspect
	// 1.2155 via rectangular cells). Fit from the measured opening (79.8% x 76.7% of the art)
	// so the opening = board minus a 4px lip per side; offsets align the art's slightly
	// off-centre opening with the board centre. (Dev candidate picker removed post sign-off.)
	const SPRITE_SCALE = { width: 1.236, height: 1.282 };
	const frameKey = 'board1';
	const frameOff = { x: 1.5, y: -3.6 };
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

<!-- The WHOLE frame block (glow, backing, frame art) rides the board-feel channels: the
     wrapper sits at the board centre, so the breath scale expands the BOARD OUTER around
     the same screen point as the symbols (BoardContainer pivots there too) and the slam
     nudge thuds frame + symbols as one body. Children draw relative to (0,0) = centre. -->
<Container
	x={context.stateGameDerived.boardLayout().x * POSITION_ADJUSTMENT + stateFx.boardNudgeX}
	y={context.stateGameDerived.boardLayout().y * POSITION_ADJUSTMENT + stateFx.boardNudgeY}
	scale={stateFx.boardScale}
>
	{#if glowActive}
		<Graphics
			blendMode="add"
			zIndex={-1}
			draw={(g) => {
				const t = trailClock.t;
				const bl = context.stateGameDerived.boardLayout();
				const w = bl.width * SPRITE_SCALE.width + 26;
				const h = bl.height * SPRITE_SCALE.height + 26;
				const breathe = 0.7 + 0.3 * Math.sin(t * Math.PI * 1.1);
				// layered halo: wide soft bloom -> mid -> tight hue ring (hues slowly cycling)
				g.roundRect(-w / 2 - 16, -h / 2 - 16, w + 32, h + 32, 34).stroke({
					width: 30,
					color: paletteAt(t * 0.16),
					alpha: 0.08 * breathe,
				});
				g.roundRect(-w / 2 - 6, -h / 2 - 6, w + 12, h + 12, 28).stroke({
					width: 12,
					color: paletteAt(t * 0.16 + 0.12),
					alpha: 0.16 * breathe,
				});
				g.roundRect(-w / 2, -h / 2, w, h, 24).stroke({
					width: 4,
					color: paletteAt(t * 0.16 + 0.24),
					alpha: 0.5 * breathe,
				});
			}}
		/>
	{/if}

	<!-- Board backing: mid-dark grey panel + light gridlines aligned to the 5x5 cells.
	     Sized off the BOARD (fixed margin), NOT the frame scale — the panel must stay tucked
	     under the frame border whatever frame/fit is selected. -->
	<Graphics
		draw={(g) => {
			const PW = BOARD_SIZES.width * 1.06;
			const PH = BOARD_SIZES.height * 1.06;
			g.roundRect(-PW / 2, -PH / 2, PW, PH, 22).fill({ color: 0x2c2c34 });
			const W = BOARD_SIZES.width;
			const H = BOARD_SIZES.height;
			for (let i = 0; i <= 5; i++) {
				const gx = -W / 2 + i * CELL_W; // rectangular cells: wider than tall
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
		x={frameOff.x}
		y={frameOff.y}
		width={context.stateGameDerived.boardLayout().width * SPRITE_SCALE.width}
		height={context.stateGameDerived.boardLayout().height * SPRITE_SCALE.height}
	/>
</Container>
