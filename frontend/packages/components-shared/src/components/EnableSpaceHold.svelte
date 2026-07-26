<script lang="ts" module>
	import { stateBet, stateBetDerived } from 'state-shared';
</script>

<script lang="ts">
	import OnHotkey from './OnHotkey.svelte';

	// the hold FORCES turbo; releasing must RESTORE the player's own toggle, not wipe it
	let turboBeforeHold = false;

	const spaceHoldOn = () => {
		stateBet.autoSpinsCounter = 0;
		stateBet.isSpaceHold = true;
		turboBeforeHold = stateBet.isTurboUser;
		stateBetDerived.updateIsTurbo(true, { persistent: true });
	};

	const spaceHoldOff = () => {
		stateBet.isSpaceHold = false;
		stateBetDerived.updateIsTurbo(turboBeforeHold, { persistent: true });
	};
</script>

<OnHotkey hotkey="Space" onhold={spaceHoldOn} onholdend={spaceHoldOff} />
