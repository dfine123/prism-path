<script lang="ts">
	// DEV-ONLY: board-frame candidate picker + live fit nudger (DOM overlay).
	// Remove this component (and stateDev / unused frame assets) once a frame is locked.
	import { stateDev, selectFrame, FRAME_OPTIONS } from '../game/stateDev.svelte';

	const nudge = (axis: 'scaleW' | 'scaleH', d: number) => {
		stateDev[axis] = Math.round((stateDev[axis] + d) * 1000) / 1000;
	};
</script>

<div class="dev-frame-panel">
	<button class="head" onclick={() => (stateDev.panelOpen = !stateDev.panelOpen)}>
		FRAME DEV {stateDev.panelOpen ? '▾' : '▸'}
	</button>
	{#if stateDev.panelOpen}
		<div class="body">
			<div class="row">
				{#each FRAME_OPTIONS as opt, i (opt.key)}
					<button class:active={stateDev.frameIndex === i} onclick={() => selectFrame(i)}>
						{opt.label}
					</button>
				{/each}
			</div>
			<div class="row">
				<span>W {stateDev.scaleW.toFixed(3)}</span>
				<button onclick={() => nudge('scaleW', -0.01)}>−</button>
				<button onclick={() => nudge('scaleW', 0.01)}>+</button>
				<span>H {stateDev.scaleH.toFixed(3)}</span>
				<button onclick={() => nudge('scaleH', -0.01)}>−</button>
				<button onclick={() => nudge('scaleH', 0.01)}>+</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.dev-frame-panel {
		position: fixed;
		top: 8px;
		right: 8px;
		z-index: 99999;
		font-family: monospace;
		font-size: 12px;
		color: #fff;
		background: rgba(10, 8, 18, 0.88);
		border: 1px solid rgba(255, 255, 255, 0.35);
		border-radius: 8px;
		padding: 4px;
		user-select: none;
	}
	.head {
		width: 100%;
		text-align: left;
	}
	.body {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin-top: 4px;
	}
	.row {
		display: flex;
		gap: 4px;
		align-items: center;
		flex-wrap: wrap;
	}
	button {
		background: #241a3a;
		color: #fff;
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 5px;
		padding: 2px 7px;
		cursor: pointer;
		font: inherit;
	}
	button:hover {
		background: #38285c;
	}
	button.active {
		background: #6a3fd4;
		border-color: #fff;
	}
	span {
		opacity: 0.85;
		min-width: 62px;
		text-align: right;
	}
</style>
