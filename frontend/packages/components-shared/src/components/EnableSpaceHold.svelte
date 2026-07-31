<script lang="ts" module>
	import { stateBet, stateBetDerived } from 'state-shared';
</script>

<script lang="ts">
	import OnHotkey from './OnHotkey.svelte';

	type Props = {
		// May the hold ARM the continuous-rebet loop right now? (Caller supplies "machine is
		// truly idle".) Omitted = always (legacy). The distinction matters: a hold that
		// begins MID-ROUND means "turbo this spin" — it must force turbo but NEVER arm
		// isSpaceHold, or the bet machine's checkSpaceHold loop fires a fresh (mode-reset)
		// bet the instant the round ends — the "bonus ends and instantly re-bets" incident.
		canArm?: () => boolean;
	};
	const props: Props = $props();

	// the hold FORCES turbo; releasing must RESTORE the player's own toggle, not wipe it
	let turboBeforeHold = false;

	const spaceHoldOn = () => {
		if (props.canArm?.() ?? true) {
			stateBet.autoSpinsCounter = 0;
			stateBet.isSpaceHold = true;
		}
		turboBeforeHold = stateBet.isTurboUser;
		stateBetDerived.updateIsTurbo(true, { persistent: true });
	};

	const spaceHoldOff = () => {
		stateBet.isSpaceHold = false;
		stateBetDerived.updateIsTurbo(turboBeforeHold, { persistent: true });
	};
</script>

<OnHotkey hotkey="Space" onhold={spaceHoldOn} onholdend={spaceHoldOff} />
