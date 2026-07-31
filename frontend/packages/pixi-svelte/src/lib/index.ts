export * from './components/index';
export * from './utils.svelte';
export * from './types';
export * from './createApp.svelte';
export * from './context.svelte';

// Pixi values that draw code legitimately needs. Consumer packages depend on pixi-svelte,
// NOT on pixi.js — importing 'pixi.js' directly from one of them fails to resolve and takes
// the whole component down (a bare `import { FillGradient } from 'pixi.js'` in UiGlass
// silently killed the entire bet console). Re-export through the sanctioned surface instead.
export { FillGradient } from 'pixi.js';
