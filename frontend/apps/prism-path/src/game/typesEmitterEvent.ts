import type { EmitterEventBoard } from '../components/Board.svelte';
import type { EmitterEventBoardFrame } from '../components/BoardFrame.svelte';
import type { EmitterEventPrismBeast } from '../components/PrismBeastTravel.svelte';
import type { EmitterEventWinLines } from '../components/WinLines.svelte';
import type { EmitterEventStickyMarkers } from '../components/StickyDragonMarkers.svelte';
import type { EmitterEventFreeSpinIntro } from '../components/FreeSpinIntro.svelte';
import type { EmitterEventFreeSpinCounter } from '../components/FreeSpinCounter.svelte';
import type { EmitterEventFreeSpinOutro } from '../components/FreeSpinOutro.svelte';
import type { EmitterEventRetriggerBanner } from '../components/RetriggerBanner.svelte';
import type { EmitterEventWin } from '../components/Win.svelte';
import type { EmitterEventSound } from '../components/Sound.svelte';
import type { EmitterEventTransition } from '../components/Transition.svelte';

export type EmitterEventGame =
	| EmitterEventBoard
	| EmitterEventBoardFrame
	| EmitterEventPrismBeast
	| EmitterEventWinLines
	| EmitterEventStickyMarkers
	| EmitterEventWin
	| EmitterEventFreeSpinIntro
	| EmitterEventFreeSpinCounter
	| EmitterEventFreeSpinOutro
	| EmitterEventRetriggerBanner
	| EmitterEventSound
	| EmitterEventTransition;
