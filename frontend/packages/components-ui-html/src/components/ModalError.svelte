<script lang="ts">
	import { Popup } from 'components-shared';
	import { zIndex } from 'constants-shared/zIndex';
	import { stateModal } from 'state-shared';

	import BaseContent from './BaseContent.svelte';

	// the raw payload is developer material — it goes to the console, never the player
	$effect(() => {
		if (stateModal.modal?.name === 'error') {
			console.error('[game] fatal error:', stateModal.modal.error);
		}
	});
</script>

{#if stateModal.modal?.name === 'error'}
	<!-- persistent: no backdrop/Escape dismiss — RELOAD is the only way out -->
	<Popup zIndex={zIndex.modal} persistent onclose={() => (stateModal.modal = null)}>
		<BaseContent maxWidth="500px">
			<div class="facet">
				<div class="card">
					<h2 class="title">SOMETHING WENT WRONG</h2>
					<p class="message">
						Something went wrong — please reload the game. Your balance is safe.
					</p>
					<button class="reload" onclick={() => window.location.reload()}>RELOAD</button>
				</div>
			</div>
		</BaseContent>
	</Popup>
{/if}

<style lang="scss">
	$cut: 16px;
	$inner: 14.5px;

	// same cut-crystal construction as the bonus cards: rim layer + plum-glass face
	.facet {
		clip-path: polygon(
			$cut 0,
			calc(100% - #{$cut}) 0,
			100% $cut,
			100% calc(100% - #{$cut}),
			calc(100% - #{$cut}) 100%,
			$cut 100%,
			0 calc(100% - #{$cut}),
			0 $cut
		);
		background: linear-gradient(180deg, rgba(217, 204, 255, 0.7), rgba(217, 204, 255, 0.22));
		padding: 1.5px;
		width: min(88vw, 380px);
	}

	.card {
		clip-path: polygon(
			$inner 0,
			calc(100% - #{$inner}) 0,
			100% $inner,
			100% calc(100% - #{$inner}),
			calc(100% - #{$inner}) 100%,
			$inner 100%,
			0 calc(100% - #{$inner}),
			0 $inner
		);
		background:
			linear-gradient(180deg, rgba(191, 168, 255, 0.13), rgba(191, 168, 255, 0) 38%),
			rgba(20, 11, 36, 0.96);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.9rem;
		text-align: center;
		padding: 1.6rem 1.4rem 1.5rem;
	}

	.title {
		font-family: 'Prism', 'Superui', sans-serif;
		font-size: 1.15rem;
		line-height: 1.35rem;
		letter-spacing: 0.02em;
		color: #fff4dc;
		text-shadow: 0 2px 0 rgba(22, 10, 36, 0.85);
		margin: 0;
	}

	.message {
		font-family: 'Superui', sans-serif;
		font-size: 0.92rem;
		line-height: 1.35rem;
		letter-spacing: 0.02em;
		color: #cdbff2;
		margin: 0;
		max-width: 30ch;
	}

	// gold crystal key, same chamfer language as the card CTAs
	.reload {
		cursor: pointer;
		border: none;
		font-family: 'Superui', sans-serif;
		font-weight: 700;
		letter-spacing: 0.16em;
		font-size: 0.9rem;
		color: #12081d;
		width: min(100%, 220px);
		min-height: 44px;
		padding: 0.62rem 0 0.58rem;
		clip-path: polygon(
			9px 0,
			calc(100% - 9px) 0,
			100% 9px,
			100% calc(100% - 9px),
			calc(100% - 9px) 100%,
			9px 100%,
			0 calc(100% - 9px),
			0 9px
		);
		background: linear-gradient(180deg, #ffeaa8 0%, #ffd25e 46%, #dc9f2e 100%);
		box-shadow:
			inset 0 1px 0 rgba(255, 255, 255, 0.6),
			inset 0 -2px 0 rgba(0, 0, 0, 0.22);
		transition:
			filter 120ms ease,
			transform 120ms ease;
	}

	.reload:hover {
		filter: brightness(1.1);
	}

	.reload:active {
		transform: scale(0.97);
	}
</style>
