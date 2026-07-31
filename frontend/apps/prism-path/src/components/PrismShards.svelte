<script lang="ts">
	// Prism-shard celebration burst — replaces the template coin fountain. Fires the game's
	// own gem sprites (H1..H4 + scatter) up from below the board centre with gravity, spin
	// and fade. Presentation-only particles (client randomness is fine here — outcomes are
	// always book-driven).
	import { onMount } from 'svelte';
	import { Container, Sprite } from 'pixi-svelte';
	import { MainContainer } from 'components-layout';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import type { WinLevelAlias } from '../game/winLevelMap';

	type Props = {
		emit?: boolean;
		levelAlias?: WinLevelAlias;
	};
	const props: Props = $props();
	const context = getContext();

	const TEXTURES = ['H1', 'H2', 'H3', 'H4', 'SCAT'];
	// particles per second by tier
	const RATE: Partial<Record<WinLevelAlias, number>> = {
		zero: 0,
		standard: 0,
		small: 6,
		nice: 10,
		substantial: 14,
		big: 26,
		superwin: 34,
		mega: 44,
		epic: 54,
		max: 70,
	};

	type Shard = {
		id: number;
		key: string;
		x: number;
		y: number;
		vx: number;
		vy: number;
		rot: number;
		vr: number;
		size: number;
		born: number;
		life: number;
	};

	let shards = $state<Shard[]>([]);
	let seq = 0;

	onMount(() => {
		let raf = 0;
		let last = performance.now();
		let carry = 0;
		const frame = () => {
			const nowT = performance.now();
			const dt = Math.min(0.05, (nowT - last) / 1000);
			last = nowT;

			const rate = props.emit ? (RATE[props.levelAlias ?? 'small'] ?? 8) : 0;
			carry += rate * dt;
			while (carry >= 1) {
				carry -= 1;
				// born HIDDEN inside the win-box footprint (this layer renders UNDER the box)
				// and flung radially with an upward bias — gems visibly erupt from behind the
				// plaque edges, arc out, then fall. Never over the text.
				const ang = Math.random() * Math.PI * 2;
				const sp = SYMBOL_SIZE * (3.2 + Math.random() * 3.2);
				shards.push({
					id: seq++,
					key: TEXTURES[Math.floor(Math.random() * TEXTURES.length)],
					x: (Math.random() - 0.5) * SYMBOL_SIZE * 2.4,
					y: (Math.random() - 0.5) * SYMBOL_SIZE * 1.2,
					vx: Math.cos(ang) * sp,
					vy: Math.sin(ang) * sp * 0.7 - SYMBOL_SIZE * 2.2,
					rot: Math.random() * Math.PI * 2,
					vr: (Math.random() - 0.5) * 7,
					size: SYMBOL_SIZE * (0.3 + Math.random() * 0.34),
					born: nowT,
					life: 1500 + Math.random() * 700,
				});
			}
			const G = SYMBOL_SIZE * 9.5;
			for (const s of shards) {
				s.vy += G * dt;
				s.x += s.vx * dt;
				s.y += s.vy * dt;
				s.rot += s.vr * dt;
			}
			shards = shards.filter((s) => nowT - s.born < s.life && s.y < SYMBOL_SIZE * 6.5);
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
		return () => cancelAnimationFrame(raf);
	});

	const alphaOf = (s: Shard) => {
		const age = (performance.now() - s.born) / s.life;
		return age < 0.75 ? 1 : Math.max(0, 1 - (age - 0.75) / 0.25);
	};
</script>

<!-- The container mounts ALWAYS, never behind an `{#if shards.length}` gate. Pixi paints in
     child-mount order, so a layer that first appears when the first shard spawns is appended
     AFTER the win box and lands in FRONT of it — which is exactly how the gems ended up over
     the BIG WIN text despite this component being ordered before the box. Keeping the
     container mounted fixes the depth for good; only the sprites come and go. -->
<MainContainer>
	<Container
		x={context.stateGameDerived.boardLayout().x}
		y={context.stateGameDerived.boardLayout().y}
	>
		{#each shards as s (s.id)}
			<Sprite
				key={s.key}
				anchor={0.5}
				x={s.x}
				y={s.y}
				rotation={s.rot}
				width={s.size}
				height={s.size}
				alpha={alphaOf(s)}
			/>
		{/each}
	</Container>
</MainContainer>
