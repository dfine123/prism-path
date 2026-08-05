import type { Howl } from 'howler';

import type { PlayOptions, GetSound, GetSoundMap } from './types';

// Music beds hand over with a short crossfade instead of a hard cut: the outgoing
// bed fades to silence while the incoming bed fades up over the same window
// (equal-power in spirit; Howler's per-voice fades are linear, and overlapping the
// two 300ms ramps reads as one continuous handover).
const CROSSFADE_MS = 300;

export function createPlayMusic<TSoundName extends string>(options: {
	howl: Howl;
	newSound: (value: TSoundName) => GetSound<TSoundName>;
	getSoundMap: () => GetSoundMap<TSoundName>;
	initSoundVolume: (soundName: TSoundName) => void;
}) {
	type Sound = GetSound<TSoundName>;

	const pauseAllMusic = () => {
		(Object.values(options.getSoundMap()) as Sound[]).forEach((existingSound) => {
			const { soundId, soundName, soundState } = existingSound;
			options.getSoundMap()[soundName] = {
				...existingSound,
				soundState: 'paused',
			};
			if (soundState !== 'playing') return;
			// fade the outgoing bed down, then park it — unless something resumed it
			// (or restarted it under a new id) while the fade was still running
			const from = options.howl.volume(soundId) as number;
			options.howl.fade(from, 0, CROSSFADE_MS, soundId);
			setTimeout(() => {
				const current = options.getSoundMap()[soundName];
				if (current?.soundId === soundId && current.soundState === 'paused') {
					options.howl.pause(soundId);
					options.initSoundVolume(soundName); // restore volume for the next resume
				}
			}, CROSSFADE_MS + 20);
		});
	};

	const fadeInMusic = (soundName: TSoundName, soundId: number) => {
		options.initSoundVolume(soundName); // seat the bed at its target volume
		const target = options.howl.volume(soundId) as number;
		options.howl.fade(0, target, CROSSFADE_MS, soundId);
	};

	const newMusic = (sound: Sound) => {
		pauseAllMusic();
		const soundId = options.howl.play(sound.soundName);
		options.getSoundMap()[sound.soundName] = {
			...sound,
			soundId,
			soundState: 'playing',
		};
		fadeInMusic(sound.soundName, soundId);
	};

	const resumeMusic = (sound: Sound) => {
		pauseAllMusic();
		options.howl.play(sound.soundId);
		options.getSoundMap()[sound.soundName] = {
			...sound,
			soundState: 'playing',
		};
		fadeInMusic(sound.soundName, sound.soundId);
	};

	const soundPlayMap = {
		new: (sound: Sound) => newMusic(sound),
		paused: (sound: Sound) => resumeMusic(sound),
		playing: (_: Sound) => {
			// Do nothing
		},
	};

	const play = (playOptions: PlayOptions<TSoundName>) => {
		const existingSound = options.getSoundMap()[playOptions.name];
		const sound = existingSound ?? options.newSound(playOptions.name);
		soundPlayMap[sound.soundState](sound);
	};

	return {
		play,
	};
}
