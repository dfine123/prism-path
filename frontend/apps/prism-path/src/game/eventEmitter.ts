import { createEventEmitter } from 'utils-event-emitter';
import type { EmitterEventHotKey } from 'components-shared';
import type { EmitterEventUi } from 'components-ui-pixi';
import type { EmitterEventModal } from 'components-ui-html';

import type { EmitterEventGame } from './typesEmitterEvent';

export type EmitterEvent =
	| EmitterEventHotKey
	| EmitterEventUi
	| EmitterEventModal
	| EmitterEventGame;

export const { eventEmitter } = createEventEmitter<EmitterEvent>();

// dev-only debug hook: lets storybook/console drive presentation events directly
// (never bundled into production builds)
if (import.meta.env.DEV && typeof window !== 'undefined') {
	(window as unknown as { __prismEmitter: typeof eventEmitter }).__prismEmitter = eventEmitter;
}
