// https://github.com/storybookjs/storybook/issues/29567
import type { StorybookConfig } from '@storybook/sveltekit';
import { mergeConfig } from 'vite';
import { fileURLToPath } from 'node:url';

import { main } from 'config-storybook';

// `pixi-svelte` is the only workspace package whose package.json `exports`/`main` point at an
// unbuilt `dist/` (the rest expose `main: ./index.ts` source). Alias it to its source entry so
// Storybook/vite compiles it directly — no dist build needed, hot-reloads on edits.
const pixiSvelteSource = fileURLToPath(
	new URL('../../../packages/pixi-svelte/index.ts', import.meta.url),
);

const config: StorybookConfig = {
	...main,
	viteFinal: async (viteConfig) =>
		mergeConfig(viteConfig, {
			resolve: {
				alias: {
					'pixi-svelte': pixiSvelteSource,
				},
			},
		}),
};

export default config;
