const DEFAULT_VOLUME_VALUE = 75;
const FALLBACK_UNMUTE_VALUE = 50;

export type VolumeKey = 'volumeValueMaster' | 'volumeValueMusic' | 'volumeValueSoundEffect';

export const stateSound = $state({
	volumeValueMaster: DEFAULT_VOLUME_VALUE,
	volumeValueMusic: DEFAULT_VOLUME_VALUE,
	volumeValueSoundEffect: DEFAULT_VOLUME_VALUE,
});

// Last non-zero level per channel, so mute/unmute round-trips the user's chosen volume
// instead of hard-resetting to a magic number. Non-reactive on purpose — it is a memo,
// not UI state.
const lastNonZeroVolume: Record<VolumeKey, number> = {
	volumeValueMaster: DEFAULT_VOLUME_VALUE,
	volumeValueMusic: DEFAULT_VOLUME_VALUE,
	volumeValueSoundEffect: DEFAULT_VOLUME_VALUE,
};

export const stateSoundHandler = {
	// call after any control sets a volume, to keep the restore point fresh
	rememberVolumeValue: (key: VolumeKey) => {
		if (stateSound[key] > 0) lastNonZeroVolume[key] = stateSound[key];
	},
	// mute keeps the level; unmute restores it (fallback only if nothing was ever set)
	toggleVolumeValue: (key: VolumeKey) => {
		stateSoundHandler.rememberVolumeValue(key);
		stateSound[key] = stateSound[key] === 0 ? lastNonZeroVolume[key] || FALLBACK_UNMUTE_VALUE : 0;
	},
};

export const stateSoundDerived = {
	volumeMaster: () => stateSound.volumeValueMaster / 100,
	volumeMusic: () => (stateSound.volumeValueMusic / 100) * stateSoundDerived.volumeMaster(),
	volumeSoundEffect: () =>
		(stateSound.volumeValueSoundEffect / 100) * stateSoundDerived.volumeMaster(),
};
