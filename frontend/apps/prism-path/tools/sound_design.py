"""Prism Path — ORIGINAL sound design, procedurally synthesized (no template audio).

Every cue is composed in code (deterministic, seeded) in one coherent WARM aesthetic:
felt-mallet / marimba-like tuned hits (lowpassed, woody, fast decay), soft
sub-supported thumps (sine pitch-drop + noise puff), breathy airy sweeps, plucked
warm tones and detuned-saw pads with slow filter motion. Musical but never glassy
or tinkly — the previous crystal-bell palette read as chimey and fatiguing.
Tunings stay diatonic (day = warm C major, free spins = darker A aeolian) so every
cue harmonizes with the beds.

Renders every cue -> assembles the Howler audio sprite the app already loads:
    static/assets/audio/sounds.json  (+ sounds.ogg / sounds.m4a / sounds.mp3)
Cue names are IDENTICAL to the existing (used) names, plus a set of NEW cues
(spin voice, count-up ticker, win stings, retrigger, buy commit, transition,
sticky claim, dismiss) that the frontend now triggers.

This script IS the provenance for the audio (no raw files to keep).

Run (needs numpy+scipy+ffmpeg):  python tools/sound_design.py
"""

import json
import os
import subprocess
import sys

import numpy as np
from scipy import signal

SR = 44100
RNG = np.random.default_rng(20260720)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "static", "assets", "audio")


# ---------------------------------------------------------------- DSP core

def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def sine(freq, dur, phase=0.0):
    return np.sin(2 * np.pi * freq * t_axis(dur) + phase)


def exp_env(dur, decay):
    """Exponential decay envelope; `decay` = time to fall to ~-60dB/1000x."""
    return np.exp(-6.907 * t_axis(dur) / decay)


def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = int(dur * SR)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    ns = max(0, n - na - nd - nr)
    env = np.concatenate([
        np.linspace(0, 1, max(na, 1), endpoint=False),
        np.linspace(1, s, max(nd, 1), endpoint=False),
        np.full(ns, s),
        np.linspace(s, 0, max(nr, 1)),
    ])
    return env[:n] if len(env) >= n else np.pad(env, (0, n - len(env)))


def lowpass(x, cutoff, order=2):
    sos = signal.butter(order, min(cutoff, SR / 2 - 100), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, cutoff, order=2):
    sos = signal.butter(order, max(cutoff, 10), "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [max(lo, 10), min(hi, SR / 2 - 100)], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_noise(dur, f_start, f_end, bw=0.5, order=2):
    """Bandpassed noise whose centre frequency sweeps f_start -> f_end (log)."""
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    # piecewise: filter in 32 chunks with interpolated centre freq (cheap time-varying BP)
    chunks = np.array_split(np.arange(n), 32)
    fc = np.geomspace(f_start, f_end, 32)
    out = np.zeros(n)
    for idx, c in zip(chunks, fc):
        lo, hi = c * (1 - bw / 2), c * (1 + bw / 2)
        out[idx] = bandpass(x, lo, hi, order)[idx]
    return out


def stereo(mono, pan=0.0):
    """Equal-power pan: -1 left .. +1 right."""
    ang = (pan + 1) * np.pi / 4
    return np.stack([mono * np.cos(ang), mono * np.sin(ang)], axis=1)


def widen(mono, amount=0.004):
    """Haas widen a mono signal into stereo."""
    d = int(amount * SR)
    left = np.pad(mono, (0, d))
    right = np.pad(mono, (d, 0))
    return np.stack([left, right], axis=1)


def reverb(x, mix=0.25, size=1.0, damp=4000.0):
    """Schroeder reverb on stereo (or mono) input; returns stereo."""
    if x.ndim == 1:
        x = stereo(x)
    combs = np.array([29.7, 31.1, 37.1, 41.4]) * 1e-3 * size
    out = np.zeros_like(x)
    for ch in range(2):
        acc = np.zeros(len(x))
        for i, cd in enumerate(combs):
            dl = int(cd * SR * (1 + 0.007 * ch * (i + 1)))
            a = np.zeros(dl + 1)
            a[0], a[-1] = 1, -0.77
            acc += signal.lfilter([1.0], a, x[:, ch])
        for ad, g in ((0.0050, 0.5), (0.0017, 0.5)):
            dl = int(ad * SR)
            b = np.zeros(dl + 1)
            a = np.zeros(dl + 1)
            b[0], b[-1] = -g, 1
            a[0], a[-1] = 1, -g
            acc = signal.lfilter(b, a, acc)
        out[:, ch] = lowpass(acc, damp)
    return x * (1 - mix) + out * mix * 0.35


def echo(x, time=0.28, fb=0.35, mix=0.3):
    if x.ndim == 1:
        x = stereo(x)
    d = int(time * SR)
    a = np.zeros(d + 1)
    a[0], a[-1] = 1, -fb
    wet = np.stack([signal.lfilter([1.0], a, x[:, 0]), signal.lfilter([1.0], a, x[:, 1])], axis=1)
    return x + (wet - x) * mix


def norm(x, peak=0.94):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def soft_limit(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def fade_io(x, fin=0.004, fout=0.02):
    n = len(x)
    ni, no = min(int(fin * SR), n // 2), min(int(fout * SR), n // 2)
    env = np.ones(n)
    if ni:
        env[:ni] = np.linspace(0, 1, ni)
    if no:
        env[-no:] = np.linspace(1, 0, no)
    return x * env[:, None] if x.ndim == 2 else x * env


def mix_into(x, i0, seg, gain=1.0):
    """Add `seg` into `x` starting at sample i0, clipping/padding safely."""
    end = min(len(x), i0 + len(seg))
    if end > i0:
        x[i0:end] += seg[: end - i0] * gain
    return x


def fold_loop(x, loop_len):
    """Wrap everything past loop_len back onto the start (reverb tails survive the wrap)."""
    n = int(loop_len * SR)
    if x.ndim == 1:
        x = stereo(x)
    out = x[:n].copy()
    tail = x[n:]
    reps = int(np.ceil(len(tail) / n)) if len(tail) else 0
    for r in range(reps):
        seg = tail[r * n:(r + 1) * n]
        out[: len(seg)] += seg
    return out


def seamless_loop(x, fade=0.035):
    """Make ANY loop truly seamless: circular crossfade of the end into the start.

    fold_loop preserves tail ENERGY across the wrap but never matches the WAVEFORM
    at the seam — for noise-based beds (spin loop, glide, anticipation) the last
    and first samples are uncorrelated, which clicked audibly on every cycle
    (the 'blip every couple seconds' in the bonus). Equal-power blend of the final
    `fade` seconds into the opening ones, then trim, so sample N-1 flows into
    sample 0 continuously. Applied to EVERY loop=True cue at build time.
    """
    if x.ndim == 1:
        x = stereo(x)
    F = min(int(fade * SR), len(x) // 4)
    if F < 8:
        return x
    t = np.linspace(0, 1, F)[:, None]
    fin = np.sin(t * np.pi / 2)
    fout = np.cos(t * np.pi / 2)
    x = x.copy()
    x[:F] = x[:F] * fin + x[-F:] * fout
    return x[:-F]


# ---------------------------------------------------------------- Instruments
#
# VOICE DESIGN NOTES (the warm palette)
#   Operator verdict on the previous pass: "too chime based and almost sound
#   annoying". The crystal-bell family (bright inharmonic partials ringing above
#   2kHz) is GONE. Every tuned hit is now a felt-mallet / marimba voice: energy
#   concentrated in the fundamental, one woody upper partial, a soft contact puff,
#   heavy lowpass — rounded and quick to decay. Weight comes from a sine pitch-drop
#   thump (120->50Hz), motion from band-crossfaded breath, sustain from detuned-saw
#   pads under a gently moving lowpass. Attacks are eased (3-8ms); nothing tinkles.

MARIMBA_PARTIALS = [(1.0, 1.0), (3.99, 0.22), (9.2, 0.055)]  # tuned-bar ratios


def soft_attack(x, ms=8.0):
    """Ease the leading edge — an instantaneous start is a click."""
    k = max(1, int(ms / 1000 * SR))
    if len(x) <= k:
        return x
    ramp = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    y = x.copy()
    y[:k] *= ramp
    return y


def marimba(freq, dur=0.42, tone=0.6, contact=0.5):
    """The kit's hero voice: a felt-struck wooden bar. Fundamental-heavy tuned
    partials, a tiny lowpassed contact puff (wood, not clank), fast decay."""
    n = int(dur * SR)
    out = np.zeros(n)
    for i, (ratio, amp) in enumerate(MARIMBA_PARTIALS):
        f = freq * ratio
        if f > SR * 0.45:
            continue
        dec = dur * (0.55 / (1 + i * 1.7))
        detune = 1 + RNG.uniform(-0.0004, 0.0004)
        out += sine(f * detune, dur) * exp_env(dur, dec) * amp * (tone ** i)
    pn = max(8, int(0.010 * SR))
    puff = lowpass(RNG.standard_normal(pn), 640) * np.linspace(1, 0, pn) ** 2
    mix_into(out, 0, puff, 0.16 * contact)
    out = lowpass(out, 850 + 2400 * tone)
    return soft_attack(out, 4)


def felt(freq, dur=0.16, tone=0.4):
    """Even softer than the marimba: a muted felt tap for UI ticks and the
    count-up ticker. Fundamental plus a whisper of octave, heavy lowpass."""
    body = (
        sine(freq, dur) * exp_env(dur, dur * 0.4)
        + sine(freq * 2.0, dur) * exp_env(dur, dur * 0.18) * 0.22 * tone
    )
    return soft_attack(lowpass(body, 900 + 1400 * tone), 4)


def thump_drop(f_hi=120.0, f_lo=50.0, dur=0.4, puff=0.5):
    """WEIGHT: a sub-supported thump — sine pitch-drop f_hi -> f_lo with a soft
    lowpassed noise puff on the front. The palette's floor, never its melody."""
    tt = t_axis(dur)
    f = f_lo + (f_hi - f_lo) * np.exp(-tt * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * exp_env(dur, dur * 0.55)
    pn = max(8, int(0.05 * SR))
    if len(x) >= pn:
        x[:pn] += lowpass(RNG.standard_normal(pn), 380) * np.linspace(1, 0, pn) ** 2 * 0.5 * puff
    return soft_attack(lowpass(x, 320), 3)


def whoosh(dur=0.55, f_lo=140.0, f_hi=900.0, curve=1.0, back=0.55):
    """AIR MOVING PAST — a bank of fixed band-passed noise layers crossfaded as
    the centre moves (no chunk-joint scratchiness). Bands sit low: body, not hiss."""
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    shape = np.sin(np.pi * tt ** curve)
    centre = f_lo + (f_hi - f_lo) * (shape * (1 - back) + tt * back)
    src = RNG.standard_normal(n)
    edges = np.geomspace(f_lo * 0.7, f_hi * 1.5, 6)
    out = np.zeros(n)
    for c in edges:
        layer = bandpass(src, c * 0.55, c * 1.8, order=2)
        w = np.exp(-((np.log(centre / c)) ** 2) / (2 * 0.55 ** 2))  # gaussian in log-f
        out += layer * w
    out += lowpass(src, 220) * 0.5
    swell = np.sin(np.pi * tt) ** 1.4
    return lowpass(out, 2200) * swell


def warm_pluck(freq, dur=0.5, tone=1300.0):
    """Karplus pluck with a DARK excitation — a warm plucked string, no zing."""
    n = int(dur * SR)
    exc = lowpass(RNG.standard_normal(int(0.012 * SR)), tone)
    buf = np.zeros(n)
    buf[:len(exc)] = exc
    delay = max(2, int(SR / freq))
    for i in range(delay, n):
        buf[i] += 0.497 * (buf[i - delay] + buf[i - delay + 1])
    return soft_attack(buf * exp_env(dur, dur * 0.4), 4)


def saw_pad(freq, dur, cutoff=850.0, lfo=0.08, lfo_depth=0.5, a=0.35, r=0.7):
    """Warm pad: four detuned saws through a gentle lowpass whose brightness
    breathes slowly (two filtered renders crossfaded by a slow LFO)."""
    tt = t_axis(dur)
    x = np.zeros(len(tt))
    for det in (-0.004, -0.0013, 0.0013, 0.004):
        ph = 2 * np.pi * freq * (1 + det) * tt + RNG.uniform(0, 2 * np.pi)
        x += signal.sawtooth(ph)
    x *= 0.25
    lo = lowpass(x, cutoff * 0.6)
    hi = lowpass(x, cutoff * 1.8)
    m = 0.5 + 0.5 * np.sin(2 * np.pi * lfo * tt + RNG.uniform(0, 2 * np.pi))
    m = 0.5 + (m - 0.5) * lfo_depth
    x = lo * (1 - m) + hi * m
    return soft_attack(x * adsr(dur, a=a, d=0.3, s=0.8, r=r), 40)


def sub_note(freq, dur):
    return sine(freq, dur) * adsr(dur, a=0.02, d=0.2, s=0.7, r=0.3)


def air_layer(dur, lo=1200.0, hi=4200.0, rate=0.12):
    """A light airy texture bed — soft banded noise, amplitude slowly breathing."""
    n = int(dur * SR)
    x = bandpass(RNG.standard_normal(n), lo, hi, order=2)
    m = 0.55 + 0.45 * np.sin(2 * np.pi * rate * t_axis(dur) + RNG.uniform(0, 2 * np.pi))
    return lowpass(x, hi) * m


# ---------------------------------------------------------------- Sequencer

def note(name):
    """'A4' -> Hz."""
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
             "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    pitch, octv = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] - 9) / 12 + (octv - 4))


def render_track(events, total_dur, pan_spread=0.0):
    """events: list of (time_sec, mono_array, gain, pan). Returns stereo."""
    n = int(total_dur * SR)
    out = np.zeros((n + SR, 2))
    for tm, x, gain, pan in events:
        s = stereo(x, pan + RNG.uniform(-pan_spread, pan_spread))
        i0 = int(tm * SR)
        seg = s[: max(0, len(out) - i0)]
        out[i0:i0 + len(seg)] += seg * gain
    return out


def warm_chord(x, i0, notes, dur, gain=1.0, spread=0.016, tone=0.6):
    """Stack marimba notes as a rolled chord — a few ms of spread reads as one
    rich warm event instead of a block hit."""
    for k, nn in enumerate(notes):
        mix_into(x, i0 + int(k * spread * SR), marimba(note(nn), dur, tone=tone), gain)


# ---------------------------------------------------------------- Music cues

DAY_CHORDS = [  # Cmaj9 . Am9 . Fmaj9 . G6(add9) — warm day realm
    ["C3", "G3", "E4", "B4", "D5"],
    ["A2", "E3", "C4", "G4", "B4"],
    ["F2", "C3", "A3", "E4", "G4"],
    ["G2", "D3", "B3", "E4", "A4"],
]
DAY_SCALE = ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5", "C6"]

NIGHT_CHORDS = [  # Am9 . Fmaj9 . Dm9 . Em7 — darker aeolian
    ["A2", "E3", "C4", "G4", "B4"],
    ["F2", "C3", "A3", "E4", "G4"],
    ["D3", "A3", "F4", "C5", "E5"],
    ["E3", "B3", "G4", "D5", "E5"],
]
NIGHT_SCALE = ["A3", "C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5"]

WIN_CHORDS = [  # C . Am . F . G — the one escalating win-bed family
    ["C3", "G3", "E4", "C5"],
    ["A2", "E3", "C4", "A4"],
    ["F2", "C3", "A3", "F4"],
    ["G2", "D3", "B3", "G4"],
]


def bgm_main():
    """Warm day bed, 48s with an A/B half so the loop doesn't fatigue: detuned-saw
    pads under a slow filter LFO, a soft bass pulse, light air, and a sparse warm
    plucked motif (marimba-doubled). The B half answers the motif a step up and
    adds a gentle marimba arp — related, but the ear notices the scenery change."""
    bpm, bars = 80.0, 16
    beat = 60.0 / bpm
    total = bars * 4 * beat  # 48s
    ev = []
    for b in range(0, bars, 2):
        chord_notes = DAY_CHORDS[(b // 2) % 4]
        tm = b * 4 * beat
        b_section = b >= 8
        cut = 980 if b_section else 800
        for i, nn in enumerate(chord_notes):
            ev.append((tm, saw_pad(note(nn), 2 * 4 * beat + 0.6, cutoff=cut, lfo=0.07), 0.045, (i - 2) * 0.25))
        # soft bass pulse: round sub on beats 1 and 3 of each bar
        for bar in range(2):
            for beat_i in (0, 2):
                t2 = tm + (bar * 4 + beat_i) * beat
                ev.append((t2, sub_note(note(chord_notes[0]) / 2, beat * 1.6), 0.115 if beat_i == 0 else 0.08, 0))
        ev.append((tm, air_layer(2 * 4 * beat, 1400, 4200, rate=0.1), 0.011, 0))
    # sparse warm plucked motif, one phrase per 4 bars; B half answers two scale steps up
    motif_deg = [(0.0, 2), (1.5, 3), (3.0, 4), (6.0, 3), (8.0, 2), (11.0, 1), (12.5, 0)]
    for cyc in (0, 4, 8, 12):
        lift = 2 if cyc >= 8 else 0
        for beat_pos, deg in motif_deg:
            if RNG.uniform() < 0.15:
                continue
            f = note(DAY_SCALE[min(deg + lift, len(DAY_SCALE) - 1)])
            tm = (cyc * 4 + beat_pos) * beat
            ev.append((tm, warm_pluck(f, beat * 2.2, tone=1500), 0.10, RNG.uniform(-0.4, 0.4)))
            ev.append((tm, marimba(f / 2, beat * 1.2, tone=0.5, contact=0.25), 0.055, 0))
    # B half: a gentle, gap-toothed marimba arp in 8ths
    for b in range(8, bars):
        chord_notes = DAY_CHORDS[(b // 2) % 4]
        tones = [note(nn) * 2 for nn in chord_notes[1:4]]
        for e in range(8):
            if RNG.uniform() < 0.45:
                continue
            tm = (b * 4 + e * 0.5) * beat
            f = tones[(e * 2 + b) % len(tones)]
            ev.append((tm, marimba(f, beat * 0.9, tone=0.5, contact=0.25), 0.05, np.sin(e) * 0.4))
    x = render_track(ev, total)
    x = echo(x, time=beat * 0.75, fb=0.28, mix=0.18)
    x = reverb(x, mix=0.28, size=1.2, damp=3800)
    return norm(fold_loop(x, total), 0.70)


def bgm_freespin():
    """Free-spins bed, 40s, darker aeolian with MORE PULSE: low saw pads breathing
    slowly, driving sub 8ths, a dark low pluck arp, marimba downbeat accents and an
    occasional low airy sweep. Same warm family as the day bed, night colours."""
    bpm, bars = 96.0, 16
    beat = 60.0 / bpm
    total = bars * 4 * beat  # 40s
    ev = []
    for b in range(0, bars, 2):
        chord_notes = NIGHT_CHORDS[(b // 2) % 4]
        tm = b * 4 * beat
        for i, nn in enumerate(chord_notes):
            ev.append((tm, saw_pad(note(nn), 2 * 4 * beat + 0.6, cutoff=580, lfo=0.09, lfo_depth=0.6), 0.05, (i - 2) * 0.25))
        # the drive: pulsing sub 8ths
        for e in range(16):
            ev.append((tm + e * beat * 0.5, sub_note(note(chord_notes[0]) / 2, beat * 0.42), 0.12 * (1.0 if e % 2 == 0 else 0.72), 0))
        ev.append((tm, air_layer(2 * 4 * beat, 900, 3200, rate=0.16), 0.013, 0))
    # dark 16th pluck arp, low register
    for b in range(bars):
        chord_notes = NIGHT_CHORDS[(b // 2) % 4]
        tones = [note(nn) for nn in chord_notes[1:]]
        pat = [0, 2, 1, 3, 0, 2, 3, 1, 0, 2, 1, 3, 2, 0, 3, 1]
        for e in range(16):
            if e % 4 == 3 and RNG.uniform() < 0.35:
                continue
            tm = (b * 4 + e * 0.25) * beat
            f = tones[pat[e] % len(tones)]
            ev.append((tm, warm_pluck(f, beat * 0.8, tone=1100), 0.075 * (1.0 if e % 4 == 0 else 0.7), np.sin(e * 1.7) * 0.5))
        ev.append((b * 4 * beat, marimba(note(chord_notes[0]) * 2, beat * 0.8, tone=0.5), 0.055, 0))
    # slow dark airy sweep each 4 bars
    for b in range(0, bars, 4):
        ev.append((b * 4 * beat, whoosh(4 * beat, 200, 1400, curve=1.3, back=0.7), 0.05, 0))
    x = render_track(ev, total)
    x = echo(x, time=beat * 0.5, fb=0.3, mix=0.2)
    x = reverb(x, mix=0.26, size=1.35, damp=3200)
    return norm(fold_loop(x, total), 0.72)


def bgm_winlevel(tier):
    """16s celebration beds — ONE escalating family (0=BIG .. 4=MAX) over the same
    C-Am-F-G progression, same voices, so tier promotions feel like the same music
    growing: pads thicken and brighten, the pluck arp densifies, marimba on-beats
    join, a motif line arrives, and MAX goes gold — deep pulse drops, octave-doubled
    melody. 120bpm, 8 bars."""
    bpm, bars = 120.0, 8
    beat = 60.0 / bpm
    total = bars * 4 * beat  # 16s
    ev = []
    cutoff = 700 + 90 * tier
    for b in range(0, bars, 2):
        chord_notes = WIN_CHORDS[(b // 2) % 4]
        tm = b * 4 * beat
        for i, nn in enumerate(chord_notes):
            ev.append((tm, saw_pad(note(nn), 2 * 4 * beat + 0.5, cutoff=cutoff, lfo=0.10 + 0.02 * tier, lfo_depth=0.5),
                       0.05 + 0.004 * tier, (i - 1.5) * 0.3))
        if tier >= 3:  # thicker: octave doubling of the top pad voice
            ev.append((tm, saw_pad(note(chord_notes[-1]) * 2, 2 * 4 * beat + 0.5, cutoff=cutoff * 1.2, lfo=0.13), 0.026, 0))
        # bass pulse in quarters; MAX adds a deep drop on each chord's downbeat
        for e in range(8):
            ev.append((tm + e * beat, sub_note(note(chord_notes[0]) / 2, beat * 0.8), 0.11 * (1.0 if e % 4 == 0 else 0.8), 0))
        if tier == 4:
            ev.append((tm, thump_drop(95, 42, 0.5, puff=0.35), 0.30, 0))
        if tier >= 2:
            ev.append((tm, air_layer(2 * 4 * beat, 1200, 3800, rate=0.2), 0.011 + 0.004 * tier, 0))
    # warm pluck arp — density rises with tier
    dens = [2, 2, 4, 4, 4][tier]
    for b in range(bars):
        chord_notes = WIN_CHORDS[(b // 2) % 4]
        tones = [note(nn) * 2 for nn in chord_notes[1:]]
        for e in range(4 * dens):
            tm = b * 4 * beat + e * beat / dens
            f = tones[(e * 2 + b) % len(tones)]
            ev.append((tm, warm_pluck(f, beat * 0.9, tone=1400 + 80 * tier), 0.068, np.sin(e * 2.1) * 0.5))
    # marimba on-beats from SUPER up
    if tier >= 1:
        for b in range(bars):
            chord_notes = WIN_CHORDS[(b // 2) % 4]
            for e in range(4):
                ev.append((b * 4 * beat + e * beat, marimba(note(chord_notes[2]), beat * 0.7, tone=0.55),
                           0.05 + 0.008 * tier, RNG.uniform(-0.3, 0.3)))
    # rising family motif from MEGA up; MAX doubles it an octave up (the gold layer)
    if tier >= 2:
        motif = [(0, 4), (2, 5), (4, 6), (6, 5), (8, 6), (12, 7), (14, 8)]
        for beat_pos, deg in motif:
            tm = beat_pos * beat * 2
            f = note(DAY_SCALE[min(deg, len(DAY_SCALE) - 1)])
            ev.append((tm, marimba(f, beat * 1.4, tone=0.6), 0.065, 0))
            if tier == 4:
                ev.append((tm, marimba(f * 2, beat * 1.2, tone=0.55), 0.042, 0))
    x = render_track(ev, total)
    x = reverb(x, mix=0.24, size=1.1, damp=3800)
    return norm(fold_loop(x, total), 0.70 + 0.02 * tier)


# ---------------------------------------------------------------- SFX cues
#
# Every cue is built from tuned voices in one key (A minor / C major family) so
# overlapping sounds during a busy spin never beat against each other.

def sfx_btn_general():
    """UI tap: one muted felt tick. Menu presses must disappear."""
    x = felt(note("A4"), 0.12, tone=0.35) * 0.8
    mix_into(x, 0, felt(note("E5"), 0.08, tone=0.25), 0.22)
    return fade_io(norm(widen(x, 0.001), 0.4))


def sfx_btn_spin():
    """Spin press: a small warm push — felt tone + a soft low nudge + a whisper of
    air. This press cue IS the spin whoosh — there is no second launch cue."""
    n = int(0.32 * SR)
    x = np.zeros(n)
    mix_into(x, 0, whoosh(0.24, 220, 800, back=0.7), 0.22)
    mix_into(x, int(0.008 * SR), felt(note("A3"), 0.2, tone=0.5), 0.6)
    mix_into(x, 0, thump_drop(110, 62, 0.14, puff=0.25), 0.3)
    return fade_io(norm(widen(x, 0.0015), 0.55))






# The five reel stops climb a gentle pentatonic ladder — one timbre family, rising
# pitch, so a full spin resolves left-to-right as a soft phrase.
REEL_STOP_NOTES = ["G3", "A3", "C4", "D4", "E4"]


def sfx_reel_stop(i):
    n = int(0.2 * SR)
    x = np.zeros(n)
    mix_into(x, 0, marimba(note(REEL_STOP_NOTES[i]), 0.18, tone=0.45, contact=0.4), 0.75)
    mix_into(x, 0, thump_drop(140, 72, 0.08, puff=0.2), 0.16)
    return fade_io(norm(widen(x, 0.001), 0.46))


# Scatters climb the shared pentatonic — the escalation the operator liked, in the
# warm voice: marimba + a plucked octave, with a little more low support each step.
SCATTER_NOTES = ["A3", "C4", "E4", "G4", "A4"]


def sfx_scatter_stop(i):
    nn = SCATTER_NOTES[i]
    dur = 0.75 + i * 0.07
    n = int((dur + 0.25) * SR)
    x = np.zeros(n)
    mix_into(x, 0, marimba(note(nn), dur, tone=0.55 + i * 0.05, contact=0.5), 0.8)
    mix_into(x, int(0.01 * SR), warm_pluck(note(nn) * 2, dur * 0.7, tone=1500), 0.3)
    mix_into(x, 0, thump_drop(120, 60, 0.14, puff=0.25), 0.14 + 0.045 * i)
    out = reverb(widen(x, 0.002), mix=0.22, size=1.0, damp=3600)
    return fade_io(norm(out, 0.58 + i * 0.03))


def sfx_dragon_glide():
    """THE GLIDE — a LOOPING flight bed, played for exactly as long as the dragon is
    travelling. Operator: the noise-only versions read THIN and SCRATCHY. The body of
    a flight is not hiss — it is MOVING AIR WITH MASS, so this is built the other way
    round: a warm tonal core (low sine + its fifth, slowly drifting = the sense of a
    big shape displacing air) carries the sound, and filtered air rides ON TOP at a
    fraction of the level, capped well below the harshness band. Slow undulation over
    a longer loop so nothing sounds like a repeating swish."""
    total = 1.6
    n = int(total * SR)
    tt = np.linspace(0, 1, n, endpoint=False)
    cyc = 2 * np.pi * tt

    # --- tonal core: the mass of the thing ---
    drift = 1 + 0.05 * np.sin(cyc)            # a slow breath in pitch
    f0 = 78.0
    core = np.sin(2 * np.pi * f0 * np.cumsum(drift) / SR) * 0.8
    core += np.sin(2 * np.pi * f0 * 1.5 * np.cumsum(drift) / SR) * 0.35   # fifth
    core += np.sin(2 * np.pi * f0 * 0.5 * np.cumsum(drift) / SR) * 0.5    # sub octave
    core = lowpass(core, 420)

    # --- air layer: soft, dark, and quiet — texture, never the subject ---
    src = RNG.standard_normal(n)
    centre = 260 * (1 + 0.35 * np.sin(cyc))   # gentler, slower sweep
    air = np.zeros(n)
    for c in np.geomspace(110, 620, 5):       # capped low: no 2kHz scratch band
        wgt = np.exp(-((np.log(centre / c)) ** 2) / (2 * 0.7 ** 2))
        air += bandpass(src, c * 0.6, c * 1.6, order=2) * wgt
    air = lowpass(air, 900)
    air *= 0.30                                # sits UNDER the core

    out = core + air
    out *= 0.88 + 0.12 * np.sin(cyc)          # slow amplitude motion
    out = lowpass(out, 1200)
    out = reverb(widen(out, 0.006), mix=0.26, size=1.2, damp=2600)
    return norm(fold_loop(out, total), 0.40)


def sfx_dragon_land():
    """DRAGON TOUCHES DOWN — a rounded warm arrival: rolled low marimba fifth with
    a felt top and a puff of air. Mid register, no ring, no glass."""
    n = int(0.6 * SR)
    x = np.zeros(n)
    warm_chord(x, 0, ["A3", "E4"], 0.5, gain=0.55, spread=0.014, tone=0.55)
    mix_into(x, int(0.02 * SR), felt(note("A4"), 0.25, tone=0.4), 0.3)
    mix_into(x, 0, whoosh(0.22, 260, 900, back=0.7), 0.16)
    out = reverb(widen(x, 0.002), mix=0.22, size=0.95, damp=3800)
    return fade_io(norm(out, 0.5))


def sfx_multiplier_landing():
    """PATH IGNITES (top layer) — a rolled warm chord rising into place over real
    body: the ONE cue for a path igniting (no second layer under it)."""
    n = int(0.9 * SR)
    x = np.zeros(n)
    warm_chord(x, 0, ["A3", "C4", "E4"], 0.75, gain=0.5, spread=0.022, tone=0.6)
    mix_into(x, int(0.09 * SR), marimba(note("A4"), 0.55, tone=0.55), 0.26)
    mix_into(x, 0, thump_drop(130, 55, 0.25, puff=0.4), 0.3)
    mix_into(x, 0, whoosh(0.35, 240, 1200, back=0.8), 0.14)
    out = reverb(widen(x, 0.0025), mix=0.24, size=1.05, damp=3800)
    return fade_io(norm(out, 0.62))




def sfx_anticipation():
    """Loopable tension (2.4s): a dark breathing saw pad over a low sub, with a
    slow airy rise — warmer and rounder than any tremolo bell could be."""
    total = 2.4
    n = int(total * SR)
    x = np.zeros(n)
    for nn, g in (("A2", 0.9), ("E3", 0.6), ("A3", 0.45), ("C4", 0.3)):
        mix_into(x, 0, saw_pad(note(nn), total, cutoff=520, lfo=1 / total, lfo_depth=0.6, a=0.05, r=0.05), g * 0.28)
    trem = 0.86 + 0.14 * np.sin(2 * np.pi * 5.0 * t_axis(total))
    x *= trem
    mix_into(x, 0, whoosh(total, 300, 1200, curve=1.4, back=0.9), 0.12)
    x += sine(note("A1"), total) * 0.16
    out = reverb(widen(x, 0.004), mix=0.28, size=1.3, damp=3000)
    return norm(fold_loop(out, total), 0.42)


def sfx_bigwin_coinloop():
    """THE COUNT-UP BED (2.8s loop): soft marimba sixteenths running a pentatonic
    figure in the mid register over a quiet warm floor — coins piling up in tune,
    an octave lower and far rounder than the old music-box run."""
    total = 2.8
    n = int(total * SR)
    x = np.zeros(n)
    step = total / 16
    seq = ["A4", "C5", "E5", "C5", "A4", "E4", "A4", "C5",
           "E5", "G5", "E5", "C5", "A4", "C5", "E5", "A5"]
    for i, nn in enumerate(seq):
        g = 0.5 if i % 4 == 0 else 0.3
        mix_into(x, int(i * step * SR), marimba(note(nn), 0.24, tone=0.5, contact=0.3), g)
    for nn in ("A2", "E3"):
        x += sine(note(nn), total) * 0.045
    out = reverb(widen(x, 0.0025), mix=0.2, size=0.95, damp=3600)
    return norm(fold_loop(out, total), 0.4)


def sfx_countup_loop():
    """Rolling-amount ticker (1.2s seamless loop): rapid SOFT felt ticks on two
    neighbour tones — motion you feel under the number, never coins or chimes."""
    total = 1.2
    n = int(total * SR)
    x = np.zeros(n)
    step = total / 16
    for i in range(16):
        f = note("G4") if i % 2 == 0 else note("A4")
        g = 0.42 if i % 4 == 0 else 0.28
        mix_into(x, int(i * step * SR), felt(f, 0.07, tone=0.3), g)
    x += sine(note("A3"), total) * 0.02  # 220Hz * 1.2s = 264 whole cycles -> seamless
    out = widen(x, 0.0012)
    return norm(fold_loop(out, total), 0.26)


def sfx_winlevel_small():
    """Per-line win: a two-note warm lift. Small, quick, survives many repeats."""
    n = int(0.45 * SR)
    x = np.zeros(n)
    mix_into(x, 0, marimba(note("E4"), 0.26, tone=0.5, contact=0.35), 0.65)
    mix_into(x, int(0.055 * SR), marimba(note("A4"), 0.3, tone=0.55, contact=0.35), 0.7)
    out = reverb(widen(x, 0.0018), mix=0.18, size=0.85, damp=3600)
    return fade_io(norm(out, 0.45))


# Win stings scale small -> large across win levels 2..5: the same marimba family
# picking up notes, weight and air as the win grows.
def sfx_win_sting(i):
    dur = [0.55, 0.7, 0.95, 1.15][i]
    n = int(dur * SR)
    x = np.zeros(n)
    if i == 0:
        mix_into(x, 0, marimba(note("C4"), 0.3, tone=0.5), 0.6)
        mix_into(x, int(0.06 * SR), marimba(note("E4"), 0.34, tone=0.55), 0.65)
    elif i == 1:
        for k, nn in enumerate(("C4", "E4", "G4")):
            mix_into(x, int(k * 0.055 * SR), marimba(note(nn), 0.38, tone=0.55), 0.6)
        mix_into(x, 0, thump_drop(110, 60, 0.14, puff=0.2), 0.16)
    elif i == 2:
        warm_chord(x, 0, ["C4", "E4", "G4"], 0.5, gain=0.5, spread=0.02, tone=0.55)
        mix_into(x, int(0.1 * SR), marimba(note("C5"), 0.45, tone=0.55), 0.34)
        mix_into(x, 0, thump_drop(120, 55, 0.2, puff=0.3), 0.24)
        mix_into(x, 0, whoosh(0.3, 220, 900, back=0.7), 0.1)
    else:
        warm_chord(x, 0, ["C4", "E4", "G4", "C5"], 0.65, gain=0.48, spread=0.02, tone=0.6)
        mix_into(x, 0, marimba(note("C3"), 0.6, tone=0.45, contact=0.3), 0.4)
        mix_into(x, 0, thump_drop(130, 50, 0.3, puff=0.4), 0.34)
        mix_into(x, 0, whoosh(0.45, 200, 1100, back=0.75), 0.14)
    out = reverb(widen(x, 0.002), mix=0.2 + 0.02 * i, size=0.9 + 0.08 * i, damp=3600)
    return fade_io(norm(out, 0.5 + 0.05 * i))


def sfx_winlevel_end():
    """Win presentation resolve: a settled warm cadence, low and round."""
    n = int(1.2 * SR)
    x = np.zeros(n)
    warm_chord(x, 0, ["E4", "A4"], 0.8, gain=0.5, spread=0.02, tone=0.55)
    mix_into(x, int(0.14 * SR), marimba(note("A3"), 0.8, tone=0.5), 0.45)
    mix_into(x, 0, thump_drop(100, 52, 0.2, puff=0.25), 0.2)
    out = reverb(widen(x, 0.0025), mix=0.24, size=1.05, damp=3400)
    return fade_io(norm(out, 0.54))


def sfx_tier_up():
    """WIN TIER RANK-UP — a fast warm two-note hand-off landing an octave up, with
    a flick of air. Quick and rounded; reads as promotion over bed + ticker."""
    n = int(0.7 * SR)
    x = np.zeros(n)
    mix_into(x, 0, marimba(note("E4"), 0.3, tone=0.6), 0.45)
    mix_into(x, int(0.07 * SR), marimba(note("A4"), 0.42, tone=0.65), 0.65)
    mix_into(x, int(0.07 * SR), warm_pluck(note("A5"), 0.3, tone=1600), 0.16)
    mix_into(x, int(0.05 * SR), whoosh(0.2, 500, 1600, back=0.8), 0.1)
    out = reverb(widen(x, 0.002), mix=0.2, size=0.95, damp=3800)
    return fade_io(norm(out, 0.55))


def sfx_near_miss():
    """SCATTER NEAR-MISS — a quiet two-note descending exhale, felt voice, short
    tail. Deliberately the DIMMEST cue in the kit."""
    n = int(0.7 * SR)
    x = np.zeros(n)
    mix_into(x, 0, felt(note("E4"), 0.3, tone=0.4), 0.5)
    mix_into(x, int(0.17 * SR), felt(note("C4"), 0.4, tone=0.35), 0.44)
    out = reverb(widen(x, 0.0015), mix=0.16, size=0.85, damp=2800)
    return fade_io(norm(out, 0.34))


def sfx_scatter_win():
    """Free spins triggered: an ascending warm fanfare that lands on the tonic —
    marimba run into a rolled chord with real body under the arrival."""
    n = int(1.8 * SR)
    x = np.zeros(n)
    for i, nn in enumerate(("A3", "C4", "E4", "A4")):
        mix_into(x, int(i * 0.1 * SR), marimba(note(nn), 0.6, tone=0.55), 0.5 + i * 0.05)
    warm_chord(x, int(0.4 * SR), ["A3", "E4", "A4", "C5"], 0.9, gain=0.42, spread=0.02, tone=0.6)
    mix_into(x, int(0.4 * SR), thump_drop(110, 50, 0.3, puff=0.4), 0.36)
    mix_into(x, int(0.35 * SR), whoosh(0.5, 200, 1200, back=0.8), 0.16)
    out = reverb(widen(x, 0.003), mix=0.26, size=1.15, damp=3600)
    return fade_io(norm(out, 0.66))


def sfx_retrigger():
    """+N FREE SPINS — its own celebratory sting (no longer reusing the trigger
    fanfare): a quick triplet run and a double accent on the tonic, bright rhythm
    in the same warm voice."""
    n = int(1.3 * SR)
    x = np.zeros(n)
    for i, nn in enumerate(("E4", "A4", "C5")):
        mix_into(x, int(i * 0.07 * SR), marimba(note(nn), 0.4, tone=0.6), 0.5)
    mix_into(x, int(0.3 * SR), marimba(note("A4"), 0.5, tone=0.65), 0.6)
    mix_into(x, int(0.42 * SR), marimba(note("A4"), 0.6, tone=0.65), 0.7)
    mix_into(x, int(0.42 * SR), warm_pluck(note("A5"), 0.5, tone=1600), 0.2)
    mix_into(x, int(0.3 * SR), thump_drop(115, 55, 0.22, puff=0.3), 0.26)
    out = reverb(widen(x, 0.0025), mix=0.24, size=1.05, damp=3800)
    return fade_io(norm(out, 0.62))


def sfx_superfreespin():
    """The transition INTO free spins: air rising, then the world opens — a deep
    warm landing chord instead of a crystal bloom."""
    n = int(3.0 * SR)
    x = np.zeros(n)
    rise_d = 1.55
    mix_into(x, 0, whoosh(rise_d, 200, 2400, curve=1.6, back=1.0), 0.45)
    tt = t_axis(rise_d)
    f = note("A3") * 2 ** (np.linspace(0, 1.6, len(tt)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    mix_into(x, 0, lowpass(np.sin(ph), 1600) * np.linspace(0.04, 0.28, len(tt)))
    i0 = int(rise_d * SR)
    mix_into(x, i0, thump_drop(90, 40, 0.5, puff=0.5), 0.75)
    warm_chord(x, i0, ["A2", "A3", "E4", "A4"], 1.1, gain=0.42, spread=0.02, tone=0.55)
    mix_into(x, i0, saw_pad(note("A3"), 1.3, cutoff=700, a=0.02, r=0.6), 0.16)
    out = reverb(widen(x, 0.003), mix=0.26, size=1.35, damp=3200)
    return fade_io(norm(out, 0.74))


def jng_intro_fs():
    """Free-spin intro jingle: a warm aeolian run resolving onto a low open chord."""
    n = int(2.2 * SR)
    x = np.zeros(n)
    run = ["A3", "C4", "E4", "A4", "C5"]
    for i, nn in enumerate(run):
        mix_into(x, int(i * 0.115 * SR), marimba(note(nn), 0.6, tone=0.55), 0.5)
        mix_into(x, int(i * 0.115 * SR), warm_pluck(note(nn) * 2, 0.4, tone=1400), 0.14)
    i0 = int(len(run) * 0.115 * SR)
    warm_chord(x, i0, ["A2", "E3", "A3", "C4", "E4"], 1.1, gain=0.38, spread=0.022, tone=0.55)
    mix_into(x, i0, thump_drop(90, 45, 0.4, puff=0.4), 0.42)
    mix_into(x, i0, whoosh(0.6, 180, 1000, back=0.7), 0.12)
    out = reverb(widen(x, 0.0025), mix=0.26, size=1.2, damp=3400)
    return fade_io(norm(out, 0.68))


def sfx_youwon_panel():
    """Feature total: a three-step warm cadence that keeps lifting (IV - V - I)."""
    n = int(2.0 * SR)
    x = np.zeros(n)
    steps = [(0.0, ["F3", "A3", "C4"]), (0.3, ["G3", "B3", "D4"]), (0.6, ["C4", "E4", "G4", "C5"])]
    for tm, ch in steps:
        warm_chord(x, int(tm * SR), ch, 0.9, gain=0.42, spread=0.016, tone=0.58)
    mix_into(x, int(0.6 * SR), thump_drop(100, 48, 0.32, puff=0.4), 0.36)
    mix_into(x, int(0.55 * SR), whoosh(0.5, 200, 1100, back=0.75), 0.12)
    out = reverb(widen(x, 0.003), mix=0.26, size=1.2, damp=3600)
    return fade_io(norm(out, 0.7))


def sfx_buy_commit():
    """BONUS BUY CONFIRMED — the game's weightiest press: a deep purchase thud with
    a short warm swell rising out of it. Commitment, not celebration."""
    n = int(1.2 * SR)
    x = np.zeros(n)
    mix_into(x, 0, thump_drop(100, 42, 0.5, puff=0.7), 0.85)
    mix_into(x, int(0.02 * SR), marimba(note("A2"), 0.7, tone=0.45, contact=0.3), 0.5)
    mix_into(x, int(0.08 * SR), saw_pad(note("A3"), 0.9, cutoff=520, a=0.12, r=0.5), 0.2)
    mix_into(x, int(0.12 * SR), marimba(note("E4"), 0.5, tone=0.5), 0.24)
    out = reverb(widen(x, 0.0025), mix=0.22, size=1.1, damp=3000)
    return fade_io(norm(out, 0.62))


def sfx_transition_whoosh():
    """Curtain in/out: one committed pass of air with a low seat — fired as the
    wipe enters and again as it releases."""
    n = int(0.7 * SR)
    x = np.zeros(n)
    mix_into(x, 0, whoosh(0.6, 220, 1500, curve=1.2, back=0.6), 0.55)
    mix_into(x, 0, lowpass(RNG.standard_normal(int(0.6 * SR)), 240) * np.sin(np.pi * np.linspace(0, 1, int(0.6 * SR))) ** 1.6, 0.22)
    return fade_io(norm(widen(x, 0.003), 0.5))


def sfx_sticky_claim():
    """A dragon CLAIMS its square — an ignite beat: low thump, a plucked warm tone
    and a rising fifth catching light, with a short breath bloom."""
    n = int(0.9 * SR)
    x = np.zeros(n)
    mix_into(x, 0, thump_drop(120, 55, 0.25, puff=0.4), 0.5)
    mix_into(x, int(0.01 * SR), warm_pluck(note("A3"), 0.5, tone=1300), 0.5)
    mix_into(x, int(0.1 * SR), marimba(note("E4"), 0.4, tone=0.55), 0.4)
    mix_into(x, int(0.2 * SR), marimba(note("A4"), 0.45, tone=0.6), 0.34)
    mix_into(x, 0, whoosh(0.35, 200, 1000, back=0.8), 0.14)
    out = reverb(widen(x, 0.0022), mix=0.22, size=1.0, damp=3600)
    return fade_io(norm(out, 0.56))


def sfx_dismiss():
    """Press-to-continue dismiss: a single soft felt tick. Nearly invisible."""
    x = felt(note("E4"), 0.11, tone=0.3) * 0.8
    return fade_io(norm(widen(x, 0.0008), 0.34))


# ---------------------------------------------------------------- Sprite build

# name -> (builder, loop?, volume)
CUES = {
    "bgm_main": (bgm_main, True, 0.55),
    "bgm_freespin": (bgm_freespin, True, 0.55),
    "bgm_winlevel_big": (lambda: bgm_winlevel(0), True, 0.6),
    "bgm_winlevel_superwin": (lambda: bgm_winlevel(1), True, 0.6),
    "bgm_winlevel_mega": (lambda: bgm_winlevel(2), True, 0.62),
    "bgm_winlevel_epic": (lambda: bgm_winlevel(3), True, 0.62),
    "bgm_winlevel_max": (lambda: bgm_winlevel(4), True, 0.65),
    "jng_intro_fs": (jng_intro_fs, False, 0.8),
    "sfx_anticipation": (sfx_anticipation, True, 0.6),
    "sfx_bigwin_coinloop": (sfx_bigwin_coinloop, True, 0.5),
    "sfx_btn_general": (sfx_btn_general, False, 0.55),
    "sfx_btn_spin": (sfx_btn_spin, False, 0.75),
    "sfx_buy_commit": (sfx_buy_commit, False, 0.75),
    "sfx_countup_loop": (sfx_countup_loop, True, 0.35),
    "sfx_dismiss": (sfx_dismiss, False, 0.4),
    "sfx_dragon_glide": (sfx_dragon_glide, True, 0.5),
    "sfx_dragon_land": (sfx_dragon_land, False, 0.62),
    "sfx_multiplier_landing": (sfx_multiplier_landing, False, 0.9),
    "sfx_near_miss": (sfx_near_miss, False, 0.5),
    "sfx_reel_stop_1": (lambda: sfx_reel_stop(0), False, 0.7),
    "sfx_reel_stop_2": (lambda: sfx_reel_stop(1), False, 0.7),
    "sfx_reel_stop_3": (lambda: sfx_reel_stop(2), False, 0.7),
    "sfx_reel_stop_4": (lambda: sfx_reel_stop(3), False, 0.7),
    "sfx_reel_stop_5": (lambda: sfx_reel_stop(4), False, 0.7),
    "sfx_retrigger": (sfx_retrigger, False, 0.8),
    "sfx_scatter_stop_1": (lambda: sfx_scatter_stop(0), False, 0.75),
    "sfx_scatter_stop_2": (lambda: sfx_scatter_stop(1), False, 0.75),
    "sfx_scatter_stop_3": (lambda: sfx_scatter_stop(2), False, 0.78),
    "sfx_scatter_stop_4": (lambda: sfx_scatter_stop(3), False, 0.8),
    "sfx_scatter_stop_5": (lambda: sfx_scatter_stop(4), False, 0.82),
    "sfx_scatter_win_v2": (sfx_scatter_win, False, 0.8),
    "sfx_sticky_claim": (sfx_sticky_claim, False, 0.7),
    "sfx_superfreespin": (sfx_superfreespin, False, 0.85),
    "sfx_tier_up": (sfx_tier_up, False, 0.75),
    "sfx_transition_whoosh": (sfx_transition_whoosh, False, 0.6),
    "sfx_win_sting_1": (lambda: sfx_win_sting(0), False, 0.6),
    "sfx_win_sting_2": (lambda: sfx_win_sting(1), False, 0.65),
    "sfx_win_sting_3": (lambda: sfx_win_sting(2), False, 0.7),
    "sfx_win_sting_4": (lambda: sfx_win_sting(3), False, 0.75),
    "sfx_winlevel_end": (sfx_winlevel_end, False, 0.7),
    "sfx_winlevel_small": (sfx_winlevel_small, False, 0.6),
    "sfx_youwon_panel": (sfx_youwon_panel, False, 0.85),
}

GAP_MS = 1000  # silence between sprite segments


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    segments = []
    sprite = {}
    cursor_ms = 0
    for name, (builder, loop, _vol) in CUES.items():
        print(f"  render {name} ...", flush=True)
        x = builder()
        if x.ndim == 1:
            x = stereo(x)
        if loop:
            # universal seam guard: every looping cue gets the circular crossfade
            x = seamless_loop(x)
            jump = float(np.max(np.abs(x[0] - x[-1])))
            print(f"    loop seam jump: {jump:.4f}")
        dur_ms = len(x) / SR * 1000
        sprite[name] = [cursor_ms, round(dur_ms, 4)] + ([True] if loop else [])
        segments.append(x)
        pad_ms = GAP_MS + (-(cursor_ms + dur_ms) % 1000)  # next cue starts on a whole second
        segments.append(np.zeros((int(pad_ms / 1000 * SR), 2)))
        cursor_ms += dur_ms + pad_ms
        cursor_ms = round(cursor_ms)
    full = np.concatenate(segments)
    full = soft_limit(full, 1.0) * 0.98

    wav_path = os.path.join(OUT_DIR, "_sounds_master.wav")
    write_wav(wav_path, full)

    for args, out_name in (
        (["-c:a", "libvorbis", "-q:a", "5"], "sounds.ogg"),
        (["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"], "sounds.m4a"),
        (["-c:a", "libmp3lame", "-b:a", "192k"], "sounds.mp3"),
    ):
        out_path = os.path.join(OUT_DIR, out_name)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", wav_path, *args, out_path], check=True)
        print(f"  wrote {out_name} ({os.path.getsize(out_path) // 1024} KB)")
    os.remove(wav_path)

    payload = {
        "sprite": sprite,
        "src": ["./assets/audio/sounds.ogg", "./assets/audio/sounds.m4a", "./assets/audio/sounds.mp3"],
        "config": {name: {"volume": vol} for name, (_b, _l, vol) in CUES.items()},
    }
    with open(os.path.join(OUT_DIR, "sounds.json"), "w") as f:
        json.dump(payload, f, indent="\t")
    print(f"  wrote sounds.json ({len(sprite)} cues, total {cursor_ms / 1000:.1f}s)")


def write_wav(path, x):
    import struct
    import wave
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    print("Prism Path sound design — synthesizing all cues")
    build()
    print("DONE")
