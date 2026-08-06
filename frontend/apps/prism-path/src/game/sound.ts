import { createSound } from 'utils-sound';

export type MusicName =
	| 'bgm_main'
	| 'bgm_freespin'
	| 'bgm_winlevel_big'
	| 'bgm_winlevel_epic'
	| 'bgm_winlevel_max'
	| 'bgm_winlevel_mega'
	| 'bgm_winlevel_superwin';

export type SoundEffectName =
	| 'jng_intro_fs'
	| 'sfx_anticipation'
	| 'sfx_bigwin_coinloop'
	| 'sfx_btn_general'
	| 'sfx_btn_spin'
	| 'sfx_buy_commit'
	| 'sfx_countup_loop'
	| 'sfx_dismiss'
	| 'sfx_dragon_glide'
	| 'sfx_dragon_land'
	| 'sfx_multiplier_landing'
	| 'sfx_near_miss'
	| 'sfx_reel_stop_1'
	| 'sfx_reel_stop_2'
	| 'sfx_reel_stop_3'
	| 'sfx_reel_stop_4'
	| 'sfx_reel_stop_5'
	| 'sfx_retrigger'
	| 'sfx_scatter_stop_1'
	| 'sfx_scatter_stop_2'
	| 'sfx_scatter_stop_3'
	| 'sfx_scatter_stop_4'
	| 'sfx_scatter_stop_5'
	| 'sfx_scatter_win_v2'
	| 'sfx_sticky_claim'
	| 'sfx_superfreespin'
	| 'sfx_tier_up'
	| 'sfx_transition_whoosh'
	| 'sfx_win_sting_1'
	| 'sfx_win_sting_2'
	| 'sfx_win_sting_3'
	| 'sfx_win_sting_4'
	| 'sfx_winlevel_end'
	| 'sfx_winlevel_small'
	| 'sfx_youwon_panel';

export type SoundName = MusicName | SoundEffectName;

const sound = createSound<SoundName>();

export { sound };
