<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { BitmapText, Container } from 'pixi-svelte';

	import { prismNumStyle, fitFontSize } from '../game/fonts';
	import { CELL_W, SYMBOL_SIZE } from '../game/constants';
	import { EASE } from '../game/motion';

	type Props = {
		x: number;
		y: number;
		multiplier: number;
		sticky: boolean;
	};

	const props: Props = $props();

	// fitFontSize caps the label to the chip's inner width, so overlap-grown values
	// ("128X") shrink to fit instead of flooding over the square
	const label = $derived(`${props.multiplier}X`);
	const fontSize = $derived(
		fitFontSize(label, props.sticky ? 34 : 50, props.sticky ? SYMBOL_SIZE * 0.62 : CELL_W * 0.76),
	);

	// A seated sticky's chip sits at the path edge (off the dragon's face); when the seat
	// goes dormant the chip GLIDES to centre instead of teleporting — an instant reposition
	// during the ignition slam read as a flash.
	const SEAT_OFFSET = SYMBOL_SIZE * 0.31;
	const seatOffset = new Tween(props.sticky ? SEAT_OFFSET : 0);
	$effect(() => {
		seatOffset.set(props.sticky ? SEAT_OFFSET : 0, { duration: 220, easing: EASE.glide });
	});

	// Pose channels. ENTRANCE pops in from small+transparent (initialized at the pop's
	// START pose — initializing at rest painted one full-size frame before the first rAF).
	// GROWTH / RE-SEAT pulses scale only: a chip that is already on screen must NEVER dip
	// its alpha — the old "reset to 0 and re-pop on every value change" was exactly the
	// blink-on-impact glitch (overlaps grow on the same beat the ignition slam hits).
	let badgeScale = $state(0.7);
	let badgeAlpha = $state(0);
	let raf = 0;

	const animateTo = (fromScale: number, fromAlpha: number) => {
		cancelAnimationFrame(raf);
		badgeScale = fromScale;
		badgeAlpha = fromAlpha;
		let lastT = performance.now();
		let el = 0;
		const POP_MS = 240;
		const frame = () => {
			const t = performance.now();
			el += t - lastT;
			lastT = t;
			const u = Math.min(1, el / POP_MS);
			badgeScale = fromScale + (1 - fromScale) * EASE.impact(u);
			badgeAlpha = Math.min(1, fromAlpha + u * 3);
			if (u < 1) raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
	};

	let mounted = false;
	let prevMult = 0;
	let prevSticky: boolean | null = null;
	$effect(() => {
		const m = props.multiplier;
		const s = props.sticky;
		if (!m) return;
		if (!mounted) {
			mounted = true;
			prevMult = m;
			prevSticky = s;
			animateTo(0.7, 0); // entrance: pop + fade in
		} else if (m !== prevMult || s !== prevSticky) {
			prevMult = m;
			prevSticky = s;
			animateTo(1.18, 1); // growth / re-seat: pulse — never transparent
		}
		return () => cancelAnimationFrame(raf);
	});
</script>

<Container x={props.x} y={props.y + seatOffset.current} scale={badgeScale} alpha={badgeAlpha}>
	<BitmapText anchor={0.5} text={label} style={prismNumStyle(fontSize)} />
</Container>
