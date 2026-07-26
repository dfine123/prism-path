import type { Snippet } from 'svelte';

import type { ButtonProps } from 'components-pixi';

type UiButtonSnippetProps = Partial<ButtonProps> & { showLabel?: boolean };

export type EmitterEventUi =
	| { type: 'hotKeySpace' }
	| { type: 'hotKeyEscape' }
	| { type: 'stopButtonClick' }
	| { type: 'stopButtonEnable' }
	| { type: 'uiShow' }
	| { type: 'uiHide' }
	| { type: 'drawerUnfold' }
	| { type: 'drawerFold' }
	| { type: 'drawerButtonShow' }
	| { type: 'drawerButtonHide' }
	// sound
	| { type: 'soundBetMode'; betModeKey: string }
	| { type: 'soundPressGeneral' }
	| { type: 'soundPressBet' }
	// bet services
	| { type: 'resumeBet' }
	| { type: 'autoBet' }
	| { type: 'bet' };

export type ButtonIcon =
	| 'decrease'
	| 'increase'
	| 'menu'
	| 'turbo'
	| 'autoSpin'
	| 'payTable'
	| 'info'
	| 'settings'
	| 'soundOn'
	| 'soundOff'
	| 'menuExit';

export type LayoutUiProps = {
	gameName: Snippet;
	logo: Snippet;
	amountBalance: Snippet<[{ stacked?: boolean; width?: number; bare?: boolean }]>;
	amountWin: Snippet<[{ stacked?: boolean; width?: number; bare?: boolean }]>;
	amountBet: Snippet<[{ stacked?: boolean; width?: number; bare?: boolean }]>;
	buttonBuyBonus: Snippet<[UiButtonSnippetProps]>;
	buttonBet: Snippet<[UiButtonSnippetProps]>;
	buttonTurbo: Snippet<[UiButtonSnippetProps]>;
	buttonAutoSpin: Snippet<[UiButtonSnippetProps]>;
	buttonIncrease: Snippet<[UiButtonSnippetProps]>;
	buttonDecrease: Snippet<[UiButtonSnippetProps]>;
	buttonMenu: Snippet<[UiButtonSnippetProps]>;
	buttonMenuClose: Snippet<[UiButtonSnippetProps]>;
	buttonPayTable: Snippet<[UiButtonSnippetProps]>;
	buttonGameRules: Snippet<[UiButtonSnippetProps]>;
	buttonSettings: Snippet<[UiButtonSnippetProps]>;
	buttonSoundSwitch: Snippet<[UiButtonSnippetProps]>;
};
