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

	// ARM ELIGIBILITY IS SAMPLED AT KEYDOWN, not when the hold engages. The same keypress
	// that begins a hold ALSO starts the bet (the console's Space handler fires on the
	// same keydown, after this component's listener — mount order puts this one first),
	// so by +400ms the machine is always mid-bet from our own press. Evaluating canArm
	// at hold time therefore NEVER passed in the normal gesture: holding Space performed
	// exactly one turbo spin and stopped — the rebet loop was functionally dead. A hold
	// that begins MID-ROUND still samples false at its keydown and never arms (the
	// "bonus ends and instantly re-bets" incident stays fixed). Sampled once per
	// gesture: keydown auto-repeat re-fires onpress and must not resample mid-bet.
	let armEligibleAtPress = false;
	let inGesture = false;

	const spacePress = () => {
		if (!inGesture) {
			inGesture = true;
			armEligibleAtPress = props.canArm?.() ?? true;
		}
	};

	const spaceHoldOn = () => {
		if (armEligibleAtPress) {
			stateBet.autoSpinsCounter = 0;
			stateBet.isSpaceHold = true;
		}
		turboBeforeHold = stateBet.isTurboUser;
		stateBetDerived.updateIsTurbo(true, { persistent: true });
	};

	const spaceHoldOff = () => {
		inGesture = false;
		armEligibleAtPress = false;
		stateBet.isSpaceHold = false;
		stateBetDerived.updateIsTurbo(turboBeforeHold, { persistent: true });
	};

	const spacePressEnd = () => {
		inGesture = false;
		armEligibleAtPress = false;
	};
</script>

<OnHotkey
	hotkey="Space"
	onpress={spacePress}
	onpressend={spacePressEnd}
	onhold={spaceHoldOn}
	onholdend={spaceHoldOff}
/>
