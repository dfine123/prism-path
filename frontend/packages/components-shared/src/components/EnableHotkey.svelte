<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	import { getContextEventEmitter } from 'utils-event-emitter';

	import type { EmitterEventHotKey } from '../types';

	const context = getContextEventEmitter<EmitterEventHotKey>();
	const PREVENT_DEFAULT_KEYS = ['Space', 'ArrowUp', 'ArrowDown'];
	const EXCLUDED_TAGS = ['input', 'textarea', 'select'];

	const getValidElement = (e: KeyboardEvent) =>
		!EXCLUDED_TAGS.includes(e?.target?.tagName?.toLowerCase());

	// physically-held keys, so a lost keyup (blur/tab-switch) can be synthesized
	const heldKeys = new Set<string>();

	function handleKeydown(e: KeyboardEvent) {
		// OS auto-repeat re-fires keydown while held — without this filter a held Space
		// "presses" again before the hold engages and instantly stops the spin it started
		if (e.repeat) return;
		if (getValidElement(e)) {
			const isSpace = e.key === ' ';
			const key = isSpace ? 'Space' : e.key;
			if (PREVENT_DEFAULT_KEYS.includes(key)) e.preventDefault();
			if (key) {
				heldKeys.add(key);
				context.eventEmitter.broadcast({ type: 'hotKey', key, action: 'keyDown' });
			}
		}
	}

	function handleKeyup(e: KeyboardEvent) {
		// keyUp is delivered UNCONDITIONALLY — the target filter applies to keydown only.
		// A keydown accepted on the canvas whose keyup lands on a focused input (e.g.
		// releasing Space over the volume slider) must still release: dropping it left
		// isSpaceHold latched true = an unattended infinite bet loop with no key held.
		const isSpace = e.key === ' ';
		const key = isSpace ? 'Space' : e.key;
		if (getValidElement(e) && PREVENT_DEFAULT_KEYS.includes(key)) e.preventDefault();
		if (key && heldKeys.has(key)) {
			heldKeys.delete(key);
			context.eventEmitter.broadcast({ type: 'hotKey', key, action: 'keyUp' });
		}
	}

	// blur / tab-switch swallows the real keyup: synthesize one for every held key so a
	// Space-hold can never keep auto-betting unattended after focus is lost
	function releaseHeldKeys() {
		for (const key of heldKeys) {
			context.eventEmitter.broadcast({ type: 'hotKey', key, action: 'keyUp' });
		}
		heldKeys.clear();
	}

	function handleVisibility() {
		if (document.visibilityState === 'hidden') releaseHeldKeys();
	}

	onMount(() => {
		window.addEventListener('keydown', handleKeydown);
		window.addEventListener('keyup', handleKeyup);
		window.addEventListener('blur', releaseHeldKeys);
		document.addEventListener('visibilitychange', handleVisibility);
	});

	onDestroy(() => {
		window.removeEventListener('keydown', handleKeydown);
		window.removeEventListener('keyup', handleKeyup);
		window.removeEventListener('blur', releaseHeldKeys);
		document.removeEventListener('visibilitychange', handleVisibility);
	});
</script>
