<script lang="ts">
	// SUPER STUDIOS BOOT — one DOM overlay, two phases, one continuous starfield:
	//   'loading' — the Super Studios brand loader (ported from the studio's reference
	//               super-studios-loading.html: cinematic starfield, wordmark with the
	//               travelling light-rainbow stroke, rainbow progress bar), driven by the
	//               REAL pixi asset progress instead of the reference's demo driver.
	//   'intro'   — the Prism Path splash: game logo, three cut-crystal feature cards
	//               (mechanic / free spins / max win) and CLICK TO CONTINUE. The continue
	//               click is also the browser's audio-unlock gesture, exactly like the old
	//               press-to-enter.
	// The starfield never restarts between phases — the loader's stage fades out and the
	// intro rises into the same sky, so the boot reads as one continuous scene.
	import { onMount } from 'svelte';

	import { getContext } from '../game/context';

	type Props = {
		onenter: () => void;
	};

	const props: Props = $props();
	const context = getContext();

	const ASSETS = {
		grain: new URL('../../assets/loader/ss_grain.png', import.meta.url).href,
		ssLogo: new URL('../../assets/loader/ss_logo.png', import.meta.url).href,
		strokeMask: new URL('../../assets/loader/ss_stroke_mask.png', import.meta.url).href,
		gameLogo: new URL('../../assets/ui/logo.png', import.meta.url).href,
		cardDragon: new URL('../../assets/ui/cards/card_bonus.png', import.meta.url).href,
		cardSticky: new URL('../../assets/ui/cards/card_super.png', import.meta.url).href,
		cardStorm: new URL('../../assets/ui/cards/card_dragon5.png', import.meta.url).href,
	};

	const CARDS = [
		{
			art: ASSETS.cardDragon,
			accent: '#2bb8e8',
			title: 'PRISM DRAGONS',
			text: 'Dragons fire paths of multiplier wilds — crossing paths MULTIPLY together.',
		},
		{
			art: ASSETS.cardSticky,
			accent: '#ffd25e',
			title: 'STICKY FREE SPINS',
			text: 'Sticky dragons claim their square and fire a fresh path every spin.',
		},
		{
			art: ASSETS.cardStorm,
			accent: '#9b3ce8',
			title: 'MAX WIN 5,000×',
			text: 'Stack the storm — every crossing multiplies toward 5,000× total bet.',
		},
	];

	let phase = $state<'loading' | 'intro' | 'leaving'>('loading');
	let sky = $state<HTMLCanvasElement | null>(null);

	const progress = $derived(Math.max(0, Math.min(100, context.stateApp.loadingProgress)));

	// loaded -> hold the full bar for a beat, then hand the sky to the intro
	$effect(() => {
		if (context.stateApp.loaded && phase === 'loading') {
			const id = setTimeout(() => (phase = 'intro'), 650);
			return () => clearTimeout(id);
		}
	});

	const enter = () => {
		if (phase !== 'intro') return;
		phase = 'leaving';
		setTimeout(() => props.onenter(), 620);
	};

	// ---------------- cinematic starfield (ported from the reference loader) ----------------
	onMount(() => {
		const canvas = sky;
		if (!canvas) return;
		const ctx = canvas.getContext('2d');
		if (!ctx) return;
		const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

		let W = 0;
		let H = 0;
		let raf = 0;
		let layers: { d: number; drift: number; stars: any[] }[] = [];
		let bokeh: any[] = [];
		let nebula: any[] = [];
		let shoot: any = null;
		let nextShoot = 2.0;
		let px = 0;
		let py = 0;
		let tpx = 0;
		let tpy = 0;

		const rnd = (a: number, b: number) => a + Math.random() * (b - a);

		const build = () => {
			const specs = [
				{ d: 0.28, dens: 7600, r: [0.4, 0.9], a: [0.16, 0.42], hero: 0, drift: 0.5 },
				{ d: 0.55, dens: 15000, r: [0.6, 1.25], a: [0.3, 0.66], hero: 0.04, drift: 1.1 },
				{ d: 1.0, dens: 42000, r: [0.9, 2.1], a: [0.55, 1.0], hero: 0.22, drift: 2.0 },
			];
			layers = specs.map((s) => {
				const n = Math.min(360, Math.round((W * H) / s.dens));
				const arr = [] as any[];
				for (let i = 0; i < n; i++) {
					const hero = Math.random() < s.hero;
					arr.push({
						x: Math.random() * W,
						y: Math.random() * H,
						r: hero ? rnd(1.4, 2.3) : rnd(s.r[0], s.r[1]),
						base: hero ? rnd(0.8, 1) : rnd(s.a[0], s.a[1]),
						sp: rnd(0.5, 1.9),
						ph: rnd(0, 6.28),
						hero,
						tint: Math.random() < 0.2 ? rnd(202, 256) : 210,
					});
				}
				return { d: s.d, drift: s.drift, stars: arr };
			});
			bokeh = [];
			const bn = Math.max(4, Math.round((W * H) / 240000));
			for (let i = 0; i < bn; i++) {
				bokeh.push({ x: Math.random() * W, y: Math.random() * H, r: rnd(7, 16), a: rnd(0.03, 0.07), d: rnd(0.35, 0.7) });
			}
			nebula = [
				{ x: W * 0.8, y: H * 0.18, r: Math.max(W, H) * 0.55, col: [96, 84, 168], a: 0.13, d: 0.3 },
				{ x: W * 0.16, y: H * 0.86, r: Math.max(W, H) * 0.5, col: [40, 96, 140], a: 0.11, d: 0.3 },
				{ x: W * 0.5, y: H * 0.5, r: Math.max(W, H) * 0.42, col: [60, 70, 120], a: 0.06, d: 0.2 },
			];
		};

		const resize = () => {
			const DPR = Math.min(window.devicePixelRatio || 1, 2);
			W = canvas.clientWidth;
			H = canvas.clientHeight;
			canvas.width = Math.round(W * DPR);
			canvas.height = Math.round(H * DPR);
			ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
			build();
		};

		const spawnShoot = () => {
			const fromTop = Math.random() < 0.5;
			shoot = {
				x: rnd(W * 0.05, W * 0.55),
				y: fromTop ? rnd(H * 0.05, H * 0.32) : rnd(H * 0.42, H * 0.72),
				sp: rnd(640, 920),
				ang: rnd(-0.6, -0.42),
				life: 0,
				dur: rnd(0.55, 0.8),
				len: rnd(95, 155),
			};
		};

		const draw = (t: number, dt: number) => {
			ctx.clearRect(0, 0, W, H);
			if (!reduce) {
				px += (tpx - px) * 0.05;
				py += (tpy - py) * 0.05;
			}
			for (const nb of nebula) {
				const gx = nb.x + px * nb.d;
				const gy = nb.y + py * nb.d;
				const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, nb.r);
				g.addColorStop(0, `rgba(${nb.col[0]},${nb.col[1]},${nb.col[2]},${nb.a})`);
				g.addColorStop(1, `rgba(${nb.col[0]},${nb.col[1]},${nb.col[2]},0)`);
				ctx.fillStyle = g;
				ctx.fillRect(0, 0, W, H);
			}
			for (const b of bokeh) {
				const g = ctx.createRadialGradient(b.x + px * b.d, b.y + py * b.d, 0, b.x + px * b.d, b.y + py * b.d, b.r);
				g.addColorStop(0, `rgba(190,205,255,${b.a})`);
				g.addColorStop(1, 'rgba(190,205,255,0)');
				ctx.fillStyle = g;
				ctx.beginPath();
				ctx.arc(b.x + px * b.d, b.y + py * b.d, b.r, 0, 6.2832);
				ctx.fill();
			}
			for (const layer of layers) {
				for (const s of layer.stars) {
					const tw = reduce ? 1 : 0.62 + 0.38 * Math.sin(t * s.sp + s.ph);
					const a = s.base * tw;
					const x = s.x + px * layer.d + ((t * layer.drift) % W) * 0;
					const y = s.y + py * layer.d;
					ctx.fillStyle = `hsla(${s.tint},68%,88%,${a})`;
					ctx.beginPath();
					ctx.arc(x, y, s.r, 0, 6.2832);
					ctx.fill();
					if (s.hero) {
						ctx.fillStyle = `hsla(${s.tint},80%,92%,${a * 0.25})`;
						ctx.beginPath();
						ctx.arc(x, y, s.r * 2.6, 0, 6.2832);
						ctx.fill();
					}
				}
			}
			if (!reduce) {
				nextShoot -= dt;
				if (!shoot && nextShoot <= 0) {
					spawnShoot();
					nextShoot = rnd(3.8, 7.8);
				}
				if (shoot) {
					shoot.life += dt;
					const p = shoot.life / shoot.dur;
					if (p >= 1) shoot = null;
					else {
						const vx = Math.cos(shoot.ang) * shoot.sp;
						const vy = Math.sin(shoot.ang) * shoot.sp;
						shoot.x += vx * dt;
						shoot.y += vy * dt;
						const tx = shoot.x - Math.cos(shoot.ang) * shoot.len;
						const ty = shoot.y - Math.sin(shoot.ang) * shoot.len;
						const f = Math.sin(Math.min(p, 1) * Math.PI);
						const g = ctx.createLinearGradient(shoot.x, shoot.y, tx, ty);
						g.addColorStop(0, `rgba(255,255,255,${0.9 * f})`);
						g.addColorStop(0.4, `rgba(210,225,255,${0.32 * f})`);
						g.addColorStop(1, 'rgba(210,225,255,0)');
						ctx.strokeStyle = g;
						ctx.lineWidth = 1.4;
						ctx.lineCap = 'round';
						ctx.beginPath();
						ctx.moveTo(shoot.x, shoot.y);
						ctx.lineTo(tx, ty);
						ctx.stroke();
						ctx.fillStyle = `rgba(255,255,255,${0.95 * f})`;
						ctx.beginPath();
						ctx.arc(shoot.x, shoot.y, 1.6, 0, 6.2832);
						ctx.fill();
					}
				}
			}
		};

		let last = performance.now();
		const frame = (now: number) => {
			const dt = Math.min(0.05, (now - last) / 1000);
			last = now;
			draw(now / 1000, dt);
			raf = requestAnimationFrame(frame);
		};
		const onMove = (e: PointerEvent) => {
			tpx = (e.clientX / window.innerWidth - 0.5) * -26;
			tpy = (e.clientY / window.innerHeight - 0.5) * -26;
		};
		window.addEventListener('resize', resize, { passive: true });
		if (!reduce) window.addEventListener('pointermove', onMove, { passive: true });
		resize();
		raf = requestAnimationFrame(frame);
		return () => {
			cancelAnimationFrame(raf);
			window.removeEventListener('resize', resize);
			window.removeEventListener('pointermove', onMove);
		};
	});
</script>

<div
	class="boot"
	class:leaving={phase === 'leaving'}
	style="--grain:url('{ASSETS.grain}'); --ss-logo:url('{ASSETS.ssLogo}'); --stroke-mask:url('{ASSETS.strokeMask}');"
	role="progressbar"
	aria-label="Loading game"
	aria-valuemin="0"
	aria-valuemax="100"
	aria-valuenow={Math.round(progress)}
>
	<canvas class="sky" bind:this={sky}></canvas>

	<!-- phase 1: the Super Studios loader -->
	<div class="stage" class:gone={phase !== 'loading'}>
		<div class="logo-outer">
			<div class="logo-wrap">
				<div class="layer bloom"></div>
				<div class="layer stroke"></div>
				<div class="layer ss-logo"></div>
				<div class="layer shine"></div>
			</div>
		</div>
		<div class="bar">
			<div class="trackwrap">
				<div class="track"><div class="fill" style="width:{progress}%"></div></div>
				<div class="head" style="left:{progress}%; opacity:{progress > 0.6 ? 1 : 0}"></div>
			</div>
			<div class="meta">
				<span class="dim">Loading<span class="dots"><b>.</b><b>.</b><b>.</b></span></span>
				<span class="pct">{Math.round(progress)}<span class="sym">%</span></span>
			</div>
		</div>
	</div>

	<!-- phase 2: the Prism Path intro -->
	{#if phase !== 'loading'}
		<div class="intro">
			<img class="game-logo" src={ASSETS.gameLogo} alt="Prism Path" draggable="false" />
			<div class="cards">
				{#each CARDS as card, i (card.title)}
					<div class="facet" style="--accent:{card.accent}; --stagger:{0.12 + i * 0.11}s">
						<div class="card">
							<div class="art">
								<img src={card.art} alt="" draggable="false" />
								<div class="art-fade"></div>
							</div>
							<h3>{card.title}</h3>
							<p>{card.text}</p>
						</div>
					</div>
				{/each}
			</div>
			<button class="continue" onclick={enter}>CLICK TO CONTINUE</button>
		</div>
	{/if}

	<div class="vignette"></div>
	<div class="grain"></div>
</div>

<style lang="scss">
	/* luminous light-rainbow (the studio ramp from the reference loader) */
	.boot {
		--c1: hsl(348 90% 82%);
		--c2: hsl(22 92% 80%);
		--c3: hsl(46 88% 81%);
		--c4: hsl(140 62% 81%);
		--c5: hsl(178 72% 83%);
		--c6: hsl(206 90% 85%);
		--c7: hsl(252 80% 86%);
		--c8: hsl(300 82% 84%);
		--ss-spin: 7s;

		position: fixed;
		inset: 0;
		z-index: 200;
		display: flex;
		align-items: center;
		justify-content: center;
		background: radial-gradient(120% 95% at 50% 42%, #070811 0%, #03040a 58%, #010206 100%);
		opacity: 0;
		animation: boot-in 0.9s ease forwards;
		transition:
			opacity 0.6s ease,
			transform 0.6s ease,
			filter 0.6s ease;

		&.leaving {
			opacity: 0;
			transform: scale(1.025);
			filter: blur(2px);
			pointer-events: none;
		}
	}
	@keyframes boot-in {
		to {
			opacity: 1;
		}
	}

	.sky {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		display: block;
	}

	.vignette {
		position: absolute;
		inset: 0;
		z-index: 1;
		pointer-events: none;
		background:
			radial-gradient(42% 34% at 50% 45%, rgba(122, 142, 205, 0.1), transparent 70%),
			radial-gradient(135% 125% at 50% 50%, transparent 50%, rgba(0, 0, 0, 0.55) 100%);
	}
	.grain {
		position: absolute;
		inset: 0;
		z-index: 2;
		pointer-events: none;
		background-image: var(--grain);
		background-size: 90px 90px;
		opacity: 0.05;
		mix-blend-mode: soft-light;
	}

	/* ---------------- phase 1: loader ---------------- */
	.stage {
		position: relative;
		z-index: 3;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: clamp(30px, 5.5vh, 58px);
		padding: 24px;
		transition:
			opacity 0.5s ease,
			transform 0.5s ease;

		&.gone {
			opacity: 0;
			transform: scale(0.985);
			pointer-events: none;
			position: absolute;
		}
	}

	.logo-outer {
		width: min(62vw, 520px);
		aspect-ratio: 1/1;
		animation: rise 0.95s cubic-bezier(0.2, 0.75, 0.2, 1) 0.15s both;
	}
	.logo-wrap {
		position: relative;
		width: 100%;
		height: 100%;
		filter: drop-shadow(0 10px 46px rgba(0, 0, 0, 0.55));
		animation: breathe 6.5s ease-in-out infinite;
	}
	.layer {
		position: absolute;
		inset: 0;
		background-repeat: no-repeat;
		background-position: center;
		background-size: contain;
	}
	.ss-logo {
		background-image: var(--ss-logo);
		z-index: 3;
		filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.18));
	}
	.stroke,
	.bloom {
		background: conic-gradient(
			from var(--ss-a),
			var(--c1),
			var(--c2),
			var(--c3),
			var(--c4),
			var(--c5),
			var(--c6),
			var(--c7),
			var(--c8),
			var(--c1)
		);
		-webkit-mask: var(--stroke-mask) center/contain no-repeat;
		mask: var(--stroke-mask) center/contain no-repeat;
		animation: rotate var(--ss-spin) linear infinite;
	}
	.stroke {
		z-index: 2;
		filter: saturate(1.04) brightness(1.05);
	}
	.bloom {
		z-index: 1;
		opacity: 0.6;
		filter: blur(12px) saturate(1.18);
		animation:
			rotate var(--ss-spin) linear infinite,
			pulse 3.4s ease-in-out infinite;
	}
	.shine {
		z-index: 4;
		mix-blend-mode: screen;
		background: linear-gradient(115deg, transparent 40%, rgba(255, 255, 255, 0.55) 50%, transparent 60%);
		background-size: 300% 100%;
		-webkit-mask: var(--ss-logo) center/contain no-repeat;
		mask: var(--ss-logo) center/contain no-repeat;
		animation: sweep 7.5s ease-in-out 1.15s infinite;
	}

	@property --ss-a {
		syntax: '<angle>';
		inherits: false;
		initial-value: 0deg;
	}
	@keyframes rotate {
		to {
			--ss-a: 360deg;
		}
	}
	@keyframes pulse {
		0%,
		100% {
			opacity: 0.42;
		}
		50% {
			opacity: 0.78;
		}
	}
	@keyframes breathe {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.012);
		}
	}
	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(16px) scale(0.965);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}
	@keyframes sweep {
		0% {
			background-position: 160% 0;
			opacity: 0;
		}
		4% {
			opacity: 0.95;
		}
		15% {
			background-position: -60% 0;
			opacity: 0;
		}
		100% {
			background-position: -60% 0;
			opacity: 0;
		}
	}

	.bar {
		width: min(66vw, 500px);
		display: flex;
		flex-direction: column;
		gap: 13px;
		animation: rise2 0.75s ease 0.55s both;
		font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
	}
	@keyframes rise2 {
		from {
			opacity: 0;
			transform: translateY(12px);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}
	.trackwrap {
		position: relative;
	}
	.track {
		position: relative;
		height: 8px;
		border-radius: 999px;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.06);
		box-shadow:
			inset 0 0 0 1px rgba(255, 255, 255, 0.04),
			inset 0 1px 2px rgba(0, 0, 0, 0.55);
	}
	.fill {
		position: absolute;
		inset: 0 auto 0 0;
		width: 0%;
		border-radius: 999px;
		background: linear-gradient(
			90deg,
			var(--c1),
			var(--c2),
			var(--c3),
			var(--c4),
			var(--c5),
			var(--c6),
			var(--c7),
			var(--c8)
		);
		box-shadow: 0 0 10px rgba(180, 200, 255, 0.35);
		transition: width 0.18s cubic-bezier(0.2, 0.7, 0.2, 1);
	}
	.head {
		position: absolute;
		top: 50%;
		left: 0%;
		width: 15px;
		height: 15px;
		transform: translate(-50%, -50%);
		border-radius: 50%;
		opacity: 0;
		background: radial-gradient(circle, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0) 68%);
		box-shadow: 0 0 12px 2px rgba(196, 214, 255, 0.7);
		transition:
			left 0.18s cubic-bezier(0.2, 0.7, 0.2, 1),
			opacity 0.3s ease;
		pointer-events: none;
	}
	.meta {
		margin-top: 2px;
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		color: rgba(236, 234, 228, 0.78);
		font-variant-numeric: tabular-nums;
	}
	.dim {
		font-size: 10.5px;
		letter-spacing: 0.34em;
		text-transform: uppercase;
		opacity: 0.5;
	}
	.dots b {
		font-weight: 400;
		opacity: 0.2;
		animation: dot 1.4s infinite;
	}
	.dots b:nth-child(2) {
		animation-delay: 0.18s;
	}
	.dots b:nth-child(3) {
		animation-delay: 0.36s;
	}
	@keyframes dot {
		0%,
		62%,
		100% {
			opacity: 0.2;
		}
		30% {
			opacity: 0.95;
		}
	}
	.pct {
		font-size: 13px;
		letter-spacing: 0.08em;
		opacity: 0.9;
	}
	.pct .sym {
		opacity: 0.45;
		margin-left: 1px;
	}

	/* ---------------- phase 2: intro splash ---------------- */
	.intro {
		position: relative;
		z-index: 3;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: clamp(14px, 3vh, 30px);
		padding: 24px;
		max-width: 1080px;
		width: 100%;
	}

	.game-logo {
		width: clamp(180px, 24vh, 260px);
		height: auto;
		filter: drop-shadow(0 8px 34px rgba(0, 0, 0, 0.6)) drop-shadow(0 0 22px rgba(155, 123, 255, 0.35));
		animation: rise 0.8s cubic-bezier(0.2, 0.75, 0.2, 1) 0.05s both;
	}

	.cards {
		display: flex;
		flex-direction: row;
		justify-content: center;
		gap: clamp(14px, 2vw, 26px);
		width: 100%;
	}

	/* the cut-crystal card language from the buy screen, on the boot sky */
	.facet {
		clip-path: polygon(
			15px 0,
			calc(100% - 15px) 0,
			100% 15px,
			100% calc(100% - 15px),
			calc(100% - 15px) 100%,
			15px 100%,
			0 calc(100% - 15px),
			0 15px
		);
		background: linear-gradient(180deg, rgba(217, 204, 255, 0.65), rgba(217, 204, 255, 0.2));
		padding: 1.5px;
		width: min(30%, 264px);
		animation: card-rise 0.7s cubic-bezier(0.2, 0.75, 0.2, 1) var(--stagger) both;
	}
	@keyframes card-rise {
		from {
			opacity: 0;
			transform: translateY(22px) scale(0.97);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}

	.card {
		display: flex;
		flex-direction: column;
		height: 100%;
		text-align: center;
		overflow: hidden;
		clip-path: polygon(
			13.5px 0,
			calc(100% - 13.5px) 0,
			100% 13.5px,
			100% calc(100% - 13.5px),
			calc(100% - 13.5px) 100%,
			13.5px 100%,
			0 calc(100% - 13.5px),
			0 13.5px
		);
		background:
			linear-gradient(180deg, rgba(191, 168, 255, 0.12), rgba(191, 168, 255, 0) 38%),
			rgba(16, 9, 28, 0.92);
		padding-bottom: 1rem;
	}

	.art {
		position: relative;
		aspect-ratio: 16 / 10;
		overflow: hidden;
		line-height: 0;
	}
	.art img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		object-position: 50% 30%;
		display: block;
	}
	.art-fade {
		position: absolute;
		inset: auto 0 -1px 0;
		height: 46%;
		background: linear-gradient(180deg, rgba(16, 9, 28, 0) 0%, rgba(16, 9, 28, 0.9) 80%, rgba(16, 9, 28, 1) 100%);
		pointer-events: none;
	}

	.card h3 {
		margin: 0.15rem 0.6rem 0.35rem;
		font-family: 'Prism', 'Superui', sans-serif;
		font-weight: 400;
		font-size: clamp(0.86rem, 1.6vw, 1.05rem);
		letter-spacing: 0.02em;
		color: var(--accent);
		text-shadow: 0 2px 0 rgba(10, 5, 20, 0.9);
	}
	.card p {
		margin: 0 0.9rem;
		font-family: 'Superui', sans-serif;
		font-size: clamp(0.68rem, 1.25vw, 0.8rem);
		letter-spacing: 0.02em;
		line-height: 1.45;
		color: #cdbff2;
	}

	.continue {
		margin-top: 0.3rem;
		font-family: 'Superui', sans-serif;
		font-weight: 700;
		font-size: 1rem;
		letter-spacing: 0.18em;
		color: #12081d;
		padding: 0.85rem 2.8rem;
		border: none;
		cursor: pointer;
		clip-path: polygon(
			12px 0,
			calc(100% - 12px) 0,
			100% 12px,
			100% calc(100% - 12px),
			calc(100% - 12px) 100%,
			12px 100%,
			0 calc(100% - 12px),
			0 12px
		);
		background: linear-gradient(180deg, #ffeaa8 0%, #ffd25e 46%, #dc9f2e 100%);
		box-shadow:
			inset 0 1px 0 rgba(255, 255, 255, 0.6),
			inset 0 -2px 0 rgba(0, 0, 0, 0.22);
		animation:
			rise2 0.7s ease 0.5s both,
			invite 2.6s ease-in-out 1.4s infinite;
		transition: filter 120ms ease;

		&:hover {
			filter: brightness(1.1);
		}
	}
	@keyframes invite {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.035);
		}
	}

	@media (max-width: 760px) {
		.cards {
			flex-direction: column;
			align-items: center;
		}
		.facet {
			width: min(86vw, 320px);
		}
		.art {
			aspect-ratio: 21 / 9;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.boot {
			animation: none;
			opacity: 1;
		}
		.logo-outer,
		.logo-wrap,
		.bar,
		.facet,
		.game-logo,
		.continue {
			animation: none;
		}
		.stroke,
		.bloom {
			animation: none;
		}
		.bloom {
			opacity: 0.7;
		}
		.shine,
		.dots b {
			animation: none;
		}
		.shine {
			opacity: 0;
		}
	}
</style>
