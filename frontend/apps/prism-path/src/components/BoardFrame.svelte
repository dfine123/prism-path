<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import { Container, Graphics, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, SYMBOL_SIZE, CELL_W } from '../game/constants';
	import { paletteAt, lerpColor, clamp01 } from '../game/motion';
	import { stateFx } from '../game/stateFx.svelte';
	import { stateGame } from '../game/stateGame.svelte';

	const context = getContext();

	// FEATURE GLOW: the frame itself signals the free-spins realm with a soft violet
	// breathing rim (the glow events were broadcast by the handlers but had no
	// subscriber — the frame gave zero feature-state signal). Eased in/out.
	let glowTarget = $state(0);
	let glow = $state(0);
	let glowT = $state(0);
	onMount(() => {
		let raf = 0;
		const frame = () => {
			glowT = performance.now() / 1000;
			glow += (glowTarget - glow) * 0.06;
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});
	context.eventEmitter.subscribeOnMount({
		boardFrameGlowShow: () => (glowTarget = 1),
		boardFrameGlowHide: () => (glowTarget = 0),
	});
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

	// Board-glass tokens (backing panel + engraved grid). One knob per visual decision so
	// the look can be tuned without touching draw code. fillAlpha < 1 is the point: the
	// sky-realm art glows through the panel instead of a flat opaque slab.
	const GLASS = {
		fill: 0x140b24, // deep violet, same family as the type treatment's plum
		fillAlpha: 0.6,
		sheen: 0xbfa8ff,
		sheenAlpha: 0.085,
		sheenSteps: 8,
		sheenDepth: 0.32, // fraction of panel height the top light reaches
		lipShade: 0x08040f,
		lipAlpha: 0.34,
		lipW: 14,
		groove: 0x0a0516,
		grooveAlpha: 0.28,
		grooveW: 3.5,
		core: 0xd9ccff,
		coreAlpha: 0.3,
		coreW: 1.4,
		inset: 7, // grid lines stop short of the panel edge
		hueAlpha: 0.12, // prism whisper on the vertical cores
		node: 0xffffff,
		nodeAlpha: 0.1,
		nodeR: 2.6,
	};

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

	<!-- FROSTED BACKDROP (operator: subtle blur behind the grid): a pre-blurred sky
	     plate masked to the panel, under the glass fill — the board reads as frosted
	     glass over the realm instead of a flat tint. Scene-aware (day / night). -->
	<Container>
		<Graphics
			isMask
			draw={(g) => {
				g.roundRect(
					(-BOARD_SIZES.width * 1.06) / 2,
					(-BOARD_SIZES.height * 1.06) / 2,
					BOARD_SIZES.width * 1.06,
					BOARD_SIZES.height * 1.06,
					22,
				).fill({ color: 0xffffff });
			}}
		/>
		<Sprite
			key={stateGame.gameType === 'basegame' ? 'blurDay' : 'blurNight'}
			anchor={0.5}
			width={BOARD_SIZES.width * 1.06}
			height={BOARD_SIZES.height * 1.06}
			alpha={0.5}
		/>
	</Container>

	<!-- Board backing: deep-violet TRANSLUCENT GLASS (the sky realm glows through) with the
	     grid drawn as engraved grooves — dark under-cut + lavender light core, inset with
	     round caps so lines never slam into the frame, verticals carrying a whisper of the
	     prism ramp, and faint facet nodes at interior crossings. Sized off the BOARD (fixed
	     margin), NOT the frame scale — the panel must stay tucked under the frame border. -->
	<Graphics
		draw={(g) => {
			const PW = BOARD_SIZES.width * 1.06;
			const PH = BOARD_SIZES.height * 1.06;
			const W = BOARD_SIZES.width;
			const H = BOARD_SIZES.height;
			const R = 22;

			// glass base — NOT fully opaque; dark enough that symbols and chips stay readable
			g.roundRect(-PW / 2, -PH / 2, PW, PH, R).fill({ color: GLASS.fill, alpha: GLASS.fillAlpha });

			// top-light sheen: stepped strips fading out by ~1/3 down. Per-step alpha deltas are
			// ~0.01 — invisible as bands, reads as light falling on the glass from the sky.
			const sheenH = PH * GLASS.sheenDepth;
			const stepH = sheenH / GLASS.sheenSteps;
			for (let s = 0; s < GLASS.sheenSteps; s++) {
				const a = GLASS.sheenAlpha * (1 - s / GLASS.sheenSteps);
				g.rect(-PW / 2 + R, -PH / 2 + 3 + s * stepH, PW - R * 2, stepH + 0.5).fill({
					color: GLASS.sheen,
					alpha: a,
				});
			}

			// inner lip shade — a soft dark ring just inside the edge seats the frame art on
			// the glass instead of the old hard panel-meets-frame cut
			g.roundRect(
				-PW / 2 + GLASS.lipW / 2,
				-PH / 2 + GLASS.lipW / 2,
				PW - GLASS.lipW,
				PH - GLASS.lipW,
				R - GLASS.lipW / 2,
			).stroke({ width: GLASS.lipW, color: GLASS.lipShade, alpha: GLASS.lipAlpha });

			// gridlines: INTERIOR only (the frame is the outer border), engraved as a dark
			// groove with a light core riding it, both stopped short of the panel edge
			const y0 = -H / 2 + GLASS.inset;
			const y1 = H / 2 - GLASS.inset;
			const x0 = -W / 2 + GLASS.inset;
			const x1 = W / 2 - GLASS.inset;
			for (let i = 1; i < 5; i++) {
				const gx = -W / 2 + i * CELL_W; // rectangular cells: wider than tall
				g.moveTo(gx, y0).lineTo(gx, y1);
				const gy = -H / 2 + i * SYMBOL_SIZE;
				g.moveTo(x0, gy).lineTo(x1, gy);
			}
			g.stroke({ width: GLASS.grooveW, color: GLASS.groove, alpha: GLASS.grooveAlpha, cap: 'round' });
			for (let i = 1; i < 5; i++) {
				const gy = -H / 2 + i * SYMBOL_SIZE;
				g.moveTo(x0, gy).lineTo(x1, gy);
			}
			g.stroke({ width: GLASS.coreW, color: GLASS.core, alpha: GLASS.coreAlpha, cap: 'round' });
			for (let i = 1; i < 5; i++) {
				// verticals get the light core PLUS a static whisper of the prism ramp — the
				// lattice reads faintly prismatic without competing with the path animation
				const gx = -W / 2 + i * CELL_W;
				g.moveTo(gx, y0).lineTo(gx, y1);
				g.stroke({ width: GLASS.coreW, color: GLASS.core, alpha: GLASS.coreAlpha, cap: 'round' });
				g.moveTo(gx, y0).lineTo(gx, y1);
				g.stroke({
					// 0.10-0.25 is the ramp's COOL band (lavender -> blue -> cyan -> teal): a
					// left-to-right prism sweep that stays in family with the violet glass —
					// the warm half of the ramp fought it
					width: GLASS.coreW + 1.2,
					color: paletteAt(0.05 + i * 0.05),
					alpha: GLASS.hueAlpha,
					cap: 'round',
				});
			}

			// facet nodes: tiny diamonds where grooves cross — the crystal-lattice tell
			for (let ix = 1; ix < 5; ix++) {
				for (let iy = 1; iy < 5; iy++) {
					const nx = -W / 2 + ix * CELL_W;
					const ny = -H / 2 + iy * SYMBOL_SIZE;
					g.poly([nx, ny - GLASS.nodeR, nx + GLASS.nodeR, ny, nx, ny + GLASS.nodeR, nx - GLASS.nodeR, ny]).fill({
						color: GLASS.node,
						alpha: GLASS.nodeAlpha,
					});
				}
			}
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

	<!-- FEATURE GLOW rim: a whisper violet aura breathing at the frame edge during
	     free spins — two soft additive strokes hugging the frame silhouette (never a
	     filled wash over the board face) -->
	{#if glow > 0.01}
		{@const FW = context.stateGameDerived.boardLayout().width * SPRITE_SCALE.width}
		{@const FH = context.stateGameDerived.boardLayout().height * SPRITE_SCALE.height}
		{@const breathe = 0.75 + 0.25 * Math.sin(glowT * Math.PI * 0.7)}
		<Graphics
			blendMode="add"
			draw={(g) => {
				g.clear();
				g.roundRect(frameOff.x - FW / 2 - 6, frameOff.y - FH / 2 - 6, FW + 12, FH + 12, 34).stroke({
					width: 10,
					color: 0x9b3ce8,
					alpha: 0.14 * glow * breathe,
				});
				g.roundRect(frameOff.x - FW / 2 - 14, frameOff.y - FH / 2 - 14, FW + 28, FH + 28, 40).stroke({
					width: 22,
					color: 0x9b3ce8,
					alpha: 0.06 * glow * breathe,
				});
			}}
		/>
	{/if}
</Container>
