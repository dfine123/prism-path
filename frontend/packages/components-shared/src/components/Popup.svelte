<script lang="ts">
	import { blur, fade } from 'svelte/transition';
	import { onMount, type Snippet } from 'svelte';

	import { waitForTimeout } from 'utils-shared/wait';

	import OnHotkey from './OnHotkey.svelte';

	type Props = {
		children: Snippet;
		zIndex: number;
		persistent?: boolean;
		// 'content' perches the close key on the top-right of the content area (default);
		// 'viewport' keeps it in the screen corner — for full-bleed layouts whose content
		// is absolutely positioned and reports no flow size (buy-bonus large/landscape)
		closeAnchor?: 'content' | 'viewport';
		onclose: () => void;
	};

	const props: Props = $props();

	const zIndexInternal = {
		topLayer: 2,
		clickToCloseLayer: 2,
		closeButton: 101,
		contentLayer: 100,
	};

	const closeModal = () => (props.persistent ? undefined : props.onclose());

	let disabled = $state(true);

	onMount(async () => {
		await waitForTimeout(300);

		disabled = false;
	});
</script>

<!-- Escape honours the same 300ms arming delay as pointer input -->
<OnHotkey hotkey="Escape" {disabled} onpress={closeModal} />

<div class="pop-up-wrap" class:disabled style={`z-index: ${props.zIndex};`}>
	<div
		class="blur-layer"
		in:fade|global={{ duration: 300 }}
		out:fade|global={{ duration: 200 }}
	></div>
	<div
		class="top-layer"
		style="--zIndex: {zIndexInternal.topLayer}"
		in:blur|global={{ duration: 300, opacity: 0 }}
		out:blur|global={{ duration: 200, opacity: 0 }}
	>
		<div
			tabindex={0}
			class="click-to-close-layer"
			onclick={closeModal}
			onkeypress={closeModal}
			role="button"
			style="--zIndex: {zIndexInternal.clickToCloseLayer}"
		></div>

		<div class="content-anchor" class:anchor-viewport={props.closeAnchor === 'viewport'}>
			{#if !props.persistent}
				<div class="close-button-wrap" style="--zIndex: {zIndexInternal.closeButton}">
					<button
						class="close-button"
						data-test="close-button"
						aria-label="Close"
						onclick={closeModal}>×</button
					>
				</div>
			{/if}
			{@render props.children()}
		</div>
	</div>
</div>

<style lang="scss">
	.pop-up-wrap {
		font-family: 'Prism', sans-serif;
		touch-action: manipulation;
		color: white;
		position: fixed;
		left: 0;
		top: 0;
		bottom: 0;
		right: 0;

		display: flex !important;
		justify-content: center;
		align-items: center;

		&.disabled {
			pointer-events: none;
		}
	}

	.blur-layer {
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		right: 0;
		background-color: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(30px);
		-webkit-backdrop-filter: blur(30px);
	}

	.top-layer {
		width: 100%;
		height: 100%;
		z-index: var(--zIndex);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.click-to-close-layer {
		z-index: var(--zIndex);

		position: absolute;
		width: 100%;
		height: 100%;
	}

	// shrink-wraps the content so the close key can anchor to ITS corner; mirrors the
	// top-layer centering so children see the same layout context as before
	.content-anchor {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		max-width: 100%;
		max-height: 100%;
		min-height: 0;
	}

	// full-bleed layouts (absolutely-positioned content with no flow size): stay
	// out of the positioning chain so the close key falls back to the viewport corner
	.content-anchor.anchor-viewport {
		position: static;
	}

	.close-button-wrap {
		position: absolute;
		top: 0;
		right: 0;
		z-index: var(--zIndex);
		// perch on the content corner, half outside the card edge
		transform: translate(38%, -38%);
	}

	.anchor-viewport .close-button-wrap {
		// viewport corner: resolves against the fixed pop-up-wrap instead
		transform: none;
		top: 0.75rem;
		right: 0.75rem;
	}

	// circular plum-glass crystal key with a lit rim on hover
	.close-button {
		cursor: pointer;
		width: 2.6rem;
		height: 2.6rem;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		font-family: 'Superui', sans-serif;
		font-size: 1.5rem;
		font-weight: 700;
		line-height: 1;
		color: #e7dcff;
		background:
			linear-gradient(180deg, rgba(191, 233, 255, 0.22), rgba(191, 233, 255, 0) 55%),
			rgba(30, 19, 52, 0.95);
		border: 1.5px solid rgba(217, 204, 255, 0.45);
		box-shadow:
			inset 0 1px 0 rgba(255, 255, 255, 0.18),
			0 2px 8px rgba(0, 0, 0, 0.35);
		transition:
			border-color 120ms ease,
			filter 120ms ease,
			transform 120ms ease;
	}

	.close-button:hover {
		border-color: #bfe9ff;
		filter: brightness(1.2);
	}

	.close-button:active {
		transform: scale(0.94);
	}
</style>
