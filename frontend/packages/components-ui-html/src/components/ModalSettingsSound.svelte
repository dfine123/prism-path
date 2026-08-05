<script lang="ts">
	import type { Snippet } from 'svelte';

	import { getContextEventEmitter } from 'utils-event-emitter';
	import { stateSound, stateSoundHandler, type VolumeKey } from 'state-shared';
	import { Button } from 'components-shared';

	import BaseIcon from './BaseIcon.svelte';
	import BaseButtonContent from './BaseButtonContent.svelte';
	import type { EmitterEventModal } from '../types';

	type Props = {
		volumeKey: VolumeKey;
		children: Snippet;
	};

	const { volumeKey, children }: Props = $props();
	const { eventEmitter } = getContextEventEmitter<EmitterEventModal>();
</script>

<div class="col">
	<span class="label">{@render children()}</span>
	<div class="row">
		<!-- mute key: remembers the level and restores it on unmute (shared handler,
		     so the pixi sound switch and this row stay in sync) -->
		<div class="button-wrap">
			<Button
				onclick={() => {
					eventEmitter.broadcast({ type: 'soundPressGeneral' });
					stateSoundHandler.toggleVolumeValue(volumeKey);
				}}
			>
				<BaseIcon width="3rem" height="3rem" />
				<BaseButtonContent>
					<span class="state-label">{stateSound[volumeKey] > 0 ? 'ON' : 'OFF'}</span>
				</BaseButtonContent>
			</Button>
		</div>

		<!-- range -->
		<input
			type="range"
			min="0"
			max="100"
			class="range"
			aria-label="volume"
			value={stateSound[volumeKey]}
			oninput={(event) => {
				stateSound[volumeKey] = Number(event.currentTarget.value);
				stateSoundHandler.rememberVolumeValue(volumeKey);
			}}
		/>

		<!-- value -->
		<div class="value">
			<span>{stateSound[volumeKey]}</span>
		</div>
	</div>
</div>

<style lang="scss">
	.col {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.label {
		font-family: 'Superui', sans-serif;
		font-size: 0.85rem;
		font-weight: 600;
		letter-spacing: 0.12em;
		color: #a79cc4;
		text-align: left;
	}

	.row {
		display: flex;
		flex-direction: row;
		gap: 0.5rem;
	}

	.button-wrap {
		width: 15%;
		display: flex;
		align-items: center;
	}

	.state-label {
		font-family: 'Superui', sans-serif;
		font-size: 0.8rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		color: #fff4dc;
	}

	.value {
		width: 15%;
		display: flex;
		justify-content: center;
		align-items: center;
		font-family: 'Superui', sans-serif;
		color: #fff4dc;
	}

	// ---- crystal slider: plum track, glass thumb, gold ring while dragging ----
	.range {
		width: 70%;
		display: flex;
		align-items: center;
		-webkit-appearance: none;
		appearance: none;
		height: 2rem;
		margin: 0;
		background: transparent;
		cursor: pointer;
		accent-color: #ffd25e; // fallback for engines that skip the vendor parts
	}

	.range:focus-visible {
		outline: 2px solid #bfe9ff;
		outline-offset: 2px;
	}

	// WebKit
	.range::-webkit-slider-runnable-track {
		height: 6px;
		border-radius: 3px;
		background: linear-gradient(180deg, rgba(15, 8, 26, 0.95), rgba(42, 27, 69, 0.95));
		border: 1px solid rgba(84, 68, 111, 0.9);
		box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5);
	}

	.range::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 18px;
		height: 18px;
		margin-top: -7px;
		border-radius: 50%;
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0) 55%),
			linear-gradient(180deg, #8a74b8, #48386a);
		border: 1.5px solid #bfe9ff;
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
		transition:
			border-color 120ms ease,
			box-shadow 120ms ease;
	}

	.range:active::-webkit-slider-thumb {
		border-color: #ffd25e;
		box-shadow: 0 0 0 3px rgba(255, 210, 94, 0.4);
	}

	// Firefox
	.range::-moz-range-track {
		height: 6px;
		border-radius: 3px;
		background: linear-gradient(180deg, rgba(15, 8, 26, 0.95), rgba(42, 27, 69, 0.95));
		border: 1px solid rgba(84, 68, 111, 0.9);
		box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5);
	}

	.range::-moz-range-thumb {
		width: 15px;
		height: 15px;
		border-radius: 50%;
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0) 55%),
			linear-gradient(180deg, #8a74b8, #48386a);
		border: 1.5px solid #bfe9ff;
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
		transition:
			border-color 120ms ease,
			box-shadow 120ms ease;
	}

	.range:active::-moz-range-thumb {
		border-color: #ffd25e;
		box-shadow: 0 0 0 3px rgba(255, 210, 94, 0.4);
	}
</style>
