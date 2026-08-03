"""Prism Path — ORIGINAL sound design, procedurally synthesized (no template audio).

Every cue is composed in code (deterministic, seeded) in one coherent aesthetic:
crystal glass bells (inharmonic FM), airy noise sweeps, soft felt thocks, dreamy
pads — day-realm major for the base game, aurora minor for free spins.

Renders every cue -> assembles the Howler audio sprite the app already loads:
    static/assets/audio/sounds.json  (+ sounds.ogg / sounds.m4a / sounds.mp3)
Cue names are IDENTICAL to the existing (used) template names, so no call-site
changes are needed. Unused template cues are dropped from the sprite.

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
    """Wrap everything past loop_len back onto the start -> seamless loop."""
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


# ---------------------------------------------------------------- Instruments
#
# VOICE DESIGN NOTES (why these sound the way they do)
#   The first pass leaned on two crutches that made everything harsh: a broadband
#   noise transient on top of each hit (reads as a CLANK / metallic pan) and a boxy
#   70-120Hz thump under cues that should be delicate. Both are gone from the small
#   cues here. Attacks are soft (5-20ms) instead of instantaneous, partials are
#   inharmonic but gently rolled off, and low end is reserved for the few moments
#   that genuinely want weight.

# Struck-bar partial ratios (bell/glass family). Higher partials decay faster, which
# is what makes a strike read as "crystal" rather than "ring modulator".
GLASS_PARTIALS = [(1.0, 1.0), (2.0, 0.5), (3.01, 0.26), (4.16, 0.13), (5.43, 0.06)]


def soft_attack(x, ms=8.0):
    """Ease the leading edge. An instantaneous start is a click, and a pile of clicks
    is exactly the 'inner workings of a computer' texture."""
    k = max(1, int(ms / 1000 * SR))
    if len(x) <= k:
        return x
    ramp = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    y = x.copy()
    y[:k] *= ramp
    return y


def bell(freq, dur=1.2, bright=1.0, warmth=1.0):
    """Crystal bell: inharmonic partials, per-partial decay, NO noise transient."""
    n = int(dur * SR)
    out = np.zeros(n)
    for i, (ratio, amp) in enumerate(GLASS_PARTIALS):
        f = freq * ratio
        if f > SR * 0.45:
            continue
        dec = dur * (0.85 / (1 + i * 1.15))
        detune = 1 + RNG.uniform(-0.0006, 0.0006)
        out += sine(f * detune, dur) * exp_env(dur, dec) * amp * (bright ** (i * 0.9))
    # a whisper of second-harmonic air instead of an FM chiff
    out += sine(freq * 2.0, dur) * exp_env(dur, dur * 0.12) * 0.08 * bright
    out = lowpass(out, 1200 + 5200 * warmth)
    return soft_attack(out, 6)


# kept as an alias so existing music code reads the same
def glass_bell(freq, dur=1.2, bright=1.0, strike=1.0):
    return bell(freq, dur, bright=bright, warmth=0.9)


def mallet(freq, dur=0.32, tone=0.6):
    """Soft wooden/crystal mallet — the count-up voice. Fundamental plus a quiet
    octave and twelfth, quick but EASED attack, no click, no noise."""
    n = int(dur * SR)
    body = (
        sine(freq, dur) * exp_env(dur, dur * 0.45)
        + sine(freq * 2.0, dur) * exp_env(dur, dur * 0.22) * 0.35 * tone
        + sine(freq * 3.01, dur) * exp_env(dur, dur * 0.12) * 0.12 * tone
    )
    return soft_attack(lowpass(body, 2200 + 3000 * tone), 5)[:n]


def whoosh(dur=0.55, f_lo=140.0, f_hi=900.0, curve=1.0, back=0.55):
    """AIR MOVING PAST — deep, smooth motion. Built by CROSSFADING a bank of fixed
    band-passed noise layers rather than re-filtering in chunks: the chunked approach
    re-computed a filter every 256 samples and butt-joined the results, and those
    discontinuities are what read as 'scratchy'. Bands sit low (140Hz-1kHz) so the
    result is body and movement, not hiss."""
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    shape = np.sin(np.pi * tt ** curve)
    centre = f_lo + (f_hi - f_lo) * (shape * (1 - back) + tt * back)
    src = RNG.standard_normal(n)
    # fixed layers spanning the range, crossfaded by proximity to the moving centre
    edges = np.geomspace(f_lo * 0.7, f_hi * 1.5, 6)
    out = np.zeros(n)
    for c in edges:
        layer = bandpass(src, c * 0.55, c * 1.8, order=2)
        w = np.exp(-((np.log(centre / c)) ** 2) / (2 * 0.55 ** 2))  # gaussian in log-f
        out += layer * w
    # a low bed underneath gives the pass real weight
    out += lowpass(src, 220) * 0.5
    swell = np.sin(np.pi * tt) ** 1.4
    return lowpass(out, 2200) * swell


def pluck(freq, dur=0.5, tone=2600.0):
    """Karplus-ish soft pluck (kept: used by the light win chime)."""
    n = int(dur * SR)
    exc = lowpass(RNG.standard_normal(int(0.012 * SR)), tone)
    buf = np.zeros(n)
    buf[:len(exc)] = exc
    delay = max(2, int(SR / freq))
    for i in range(delay, n):
        buf[i] += 0.497 * (buf[i - delay] + buf[i - delay + 1])
    return soft_attack(buf * exp_env(dur, dur * 0.4), 4)


def pad_note(freq, dur, tone=1400.0):
    x = (sine(freq * 0.999, dur) + sine(freq * 1.001, dur) + sine(freq * 2, dur) * 0.3)
    return soft_attack(lowpass(x, tone) * adsr(dur, a=0.12, d=0.3, s=0.75, r=0.35), 40)


def sub_note(freq, dur):
    return sine(freq, dur) * adsr(dur, a=0.02, d=0.2, s=0.7, r=0.3)


def body_hit(freq=110.0, dur=0.3, drop=0.5, warm=1.0):
    """WEIGHT, not a pan strike. A pitched drop with the click rolled off — used only
    where impact is genuinely wanted, and always well under the musical layer."""
    tt = t_axis(dur)
    f = freq * (1 + drop * np.exp(-tt * 22))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * exp_env(dur, dur * 0.3)
    return soft_attack(lowpass(x, 220 * warm), 6)


# legacy name used by the music section
def thump(freq=95.0, dur=0.35, drop=0.5):
    return body_hit(freq, dur, drop)


def shimmer(dur, density=18.0, f_lo=2400.0, f_hi=7000.0, decay_each=0.22):
    """A sparse cloud of tuned micro-bells. Tuned (not random) frequencies and a
    LOW density: the old version fired ~30 random impulses a second across four
    octaves, which is precisely why it read as static/machine noise."""
    n = int(dur * SR)
    out = np.zeros(n + int(0.4 * SR))
    scale = np.array([0, 2, 4, 7, 9])  # major pentatonic — no dissonant collisions
    count = max(1, int(dur * density))
    for _ in range(count):
        tm = RNG.uniform(0, dur)
        octv = RNG.integers(0, 3)
        semi = scale[RNG.integers(0, len(scale))] + 12 * octv
        f = f_lo * 2 ** (semi / 12)
        if f > f_hi:
            f /= 2
        d = RNG.uniform(0.08, decay_each)
        seg = mallet(f, d, tone=0.35) * RNG.uniform(0.25, 0.7)
        i0 = int(tm * SR)
        out[i0:i0 + len(seg)] += seg
    return out[:n + int(0.4 * SR)]


# legacy alias (music cues call glitter)
def glitter(dur, density=28.0, f_lo=1800.0, f_hi=7500.0, decay_each=0.18):
    return shimmer(dur, density=density * 0.5, f_lo=f_lo, f_hi=f_hi, decay_each=decay_each)


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


# ---------------------------------------------------------------- Music cues

DAY_CHORDS = [  # Cmaj9 . Am9 . Fmaj9 . G6(add9) — dreamy day realm
    ["C3", "G3", "E4", "B4", "D5"],
    ["A2", "E3", "C4", "G4", "B4"],
    ["F2", "C3", "A3", "E4", "G4"],
    ["G2", "D3", "B3", "E4", "A4"],
]
DAY_SCALE = ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5", "C6"]

NIGHT_CHORDS = [  # Am9 . Fmaj7 . Cmaj7 . Em7 — aurora
    ["A2", "E3", "C4", "G4", "B4"],
    ["F2", "C3", "A3", "E4", "G4"],
    ["C3", "G3", "E4", "B4", "D5"],
    ["E3", "B3", "G4", "D5", "E5"],
]
NIGHT_SCALE = ["A3", "C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5"]


def bgm_main():
    bpm, bars = 80.0, 16
    beat = 60.0 / bpm
    total = bars * 4 * beat  # 48s
    ev = []
    # pads: one chord per 2 bars, cycling
    for b in range(0, bars, 2):
        chord = DAY_CHORDS[(b // 2) % 4]
        tm = b * 4 * beat
        for i, nn in enumerate(chord):
            ev.append((tm, pad_note(note(nn), 2 * 4 * beat + 0.5), 0.055, (i - 2) * 0.25))
        ev.append((tm, sub_note(note(chord[0]) / 2, 2 * 4 * beat), 0.14, 0))
    # arp: gentle 8ths over chord tones, skips for air
    for b in range(bars):
        chord = DAY_CHORDS[(b // 2) % 4]
        tones = [note(nn) * 2 for nn in chord[1:]] + [note(chord[2]) * 4]
        for e in range(8):
            if RNG.uniform() < 0.22:
                continue
            tm = (b * 4 + e * 0.5) * beat
            f = tones[(e * 3 + b) % len(tones)]
            ev.append((tm, pluck(f, beat * 1.6, tone=2200), 0.10 * RNG.uniform(0.7, 1.0), np.sin(e) * 0.4))
    # sparse bell motif: one phrase each 4 bars
    motif_deg = [(0.0, 4), (1.0, 6), (2.0, 5), (3.5, 7), (6.0, 8), (10.0, 5), (12.0, 6), (14.0, 4)]
    for cyc in (0, 8):
        for beat_pos, deg in motif_deg:
            tm = (cyc * 4 + beat_pos) * beat
            if cyc == 8:
                deg = min(deg + 1, len(DAY_SCALE) - 1)
            ev.append((tm, glass_bell(note(DAY_SCALE[deg]), 2.2, bright=0.8, strike=0.4), 0.075, RNG.uniform(-0.5, 0.5)))
    x = render_track(ev, total)
    x = echo(x, time=beat * 0.75, fb=0.3, mix=0.22)
    x = reverb(x, mix=0.34, size=1.25, damp=5200)
    return norm(fold_loop(x, total), 0.70)


def bgm_freespin():
    bpm, bars = 96.0, 16
    beat = 60.0 / bpm
    total = bars * 4 * beat  # 40s
    ev = []
    for b in range(0, bars, 2):
        chord = NIGHT_CHORDS[(b // 2) % 4]
        tm = b * 4 * beat
        for i, nn in enumerate(chord):
            ev.append((tm, pad_note(note(nn), 2 * 4 * beat + 0.5, tone=1100), 0.06, (i - 2) * 0.25))
        # pulsing sub 8ths
        for e in range(16):
            ev.append((tm + e * beat * 0.5, sub_note(note(chord[0]) / 2, beat * 0.42), 0.11 * (1.0 if e % 2 == 0 else 0.7), 0))
    # driving 16th arp
    for b in range(bars):
        chord = NIGHT_CHORDS[(b // 2) % 4]
        tones = [note(nn) * 2 for nn in chord[1:]]
        pat = [0, 2, 1, 3, 0, 2, 3, 1, 0, 2, 1, 3, 2, 0, 3, 1]
        for e in range(16):
            if e % 4 == 3 and RNG.uniform() < 0.3:
                continue
            tm = (b * 4 + e * 0.25) * beat
            f = tones[pat[e] % len(tones)]
            ev.append((tm, pluck(f, beat * 0.9, tone=2600), 0.085 * (1.0 if e % 4 == 0 else 0.75), np.sin(e * 1.7) * 0.5))
    # aurora shimmer sweep each 4 bars + night bell answers
    for b in range(0, bars, 4):
        tm = b * 4 * beat
        ev.append((tm, sweep_noise(4 * beat, 900, 5200, bw=0.4), 0.028, 0))
        for beat_pos, deg in ((8.0, 7), (10.0, 9), (11.0, 8), (14.0, 10)):
            ev.append(((b * 4 + beat_pos) * beat, glass_bell(note(NIGHT_SCALE[deg % len(NIGHT_SCALE)]), 1.8, bright=0.9, strike=0.3), 0.07, RNG.uniform(-0.5, 0.5)))
    x = render_track(ev, total)
    x = echo(x, time=beat * 0.5, fb=0.34, mix=0.24)
    x = reverb(x, mix=0.3, size=1.4, damp=4600)
    return norm(fold_loop(x, total), 0.72)


def bgm_winlevel(tier):
    """8s celebration loops, escalating: 0=big..4=max. 120bpm, 4 bars."""
    bpm, bars = 120.0, 4
    beat = 60.0 / bpm
    total = bars * 4 * beat  # 8s
    chords = [["C3", "G3", "E4", "C5"], ["F3", "C4", "A4", "F5"],
              ["G3", "D4", "B4", "G5"], ["C3", "G3", "E4", "C5"]]
    ev = []
    dens = [2, 2, 4, 4, 4][tier]           # arp notes per beat
    octv = [1, 1, 2, 2, 2][tier]           # arp octave lift
    layers = tier + 1
    for b in range(bars):
        chord = chords[b]
        tm = b * 4 * beat
        for i, nn in enumerate(chord):
            ev.append((tm, pad_note(note(nn), 4 * beat + 0.3, tone=1800), 0.06, (i - 1.5) * 0.3))
        ev.append((tm, sub_note(note(chord[0]) / 2, 4 * beat), 0.13, 0))
        for e in range(4 * dens):
            tm2 = tm + e * beat / dens
            f = note(chord[1 + (e % 3)]) * octv
            ev.append((tm2, pluck(f, beat, tone=3000), 0.09, np.sin(e * 2.1) * 0.5))
        if layers >= 2:  # bell hits on beats
            for e in range(4):
                ev.append((tm + e * beat, glass_bell(note(chord[2]) * 2, 0.9, bright=0.9), 0.05 * (1 + 0.15 * tier), RNG.uniform(-0.4, 0.4)))
        if layers >= 4:  # glitter bed
            ev.append((tm, glitter(4 * beat, density=10 + 6 * tier), 0.035, 0))
    if tier == 4:  # max: triumphant high line
        for e, deg in ((0, 8), (2, 9), (4, 10), (6, 9), (8, 10), (12, 10)):
            ev.append((e * beat, glass_bell(note(DAY_SCALE[deg]), 1.6, bright=1.05), 0.075, 0))
    x = render_track(ev, total)
    x = reverb(x, mix=0.26, size=1.1, damp=5600)
    return norm(fold_loop(x, total), 0.72 + 0.02 * tier)


# ---------------------------------------------------------------- SFX cues
#
# Every cue below is built from tuned voices in one key (A minor / C major family) so
# that overlapping sounds during a busy spin never beat against each other.

def chord(x, i0, notes, dur, gain=1.0, spread=0.012, bright=0.9, warmth=1.0):
    """Stack notes as a rolled chord — a few ms of spread reads as one rich event."""
    for k, nn in enumerate(notes):
        mix_into(x, i0 + int(k * spread * SR), bell(note(nn), dur, bright=bright, warmth=warmth), gain)


def sfx_btn_general():
    """UI tap: a soft muted mallet. No bell ring — menu presses must disappear."""
    x = mallet(note("A5"), 0.13, tone=0.35) * 0.8
    mix_into(x, 0, mallet(note("E6"), 0.09, tone=0.2), 0.3)
    return fade_io(norm(widen(x, 0.001), 0.42))


def sfx_btn_spin():
    """Spin press: a short intake of air + a soft confirm tone. The launch itself is
    carried by the reels, so this stays small and non-percussive."""
    n = int(0.34 * SR)
    x = np.zeros(n)
    mix_into(x, 0, whoosh(0.28, 700, 2100, back=0.8), 0.30)
    mix_into(x, int(0.01 * SR), mallet(note("A4"), 0.22, tone=0.55), 0.55)
    mix_into(x, int(0.01 * SR), mallet(note("E5"), 0.20, tone=0.45), 0.35)
    mix_into(x, 0, body_hit(120, 0.16, drop=0.4), 0.30)
    return fade_io(norm(widen(x, 0.0015), 0.6))


def sfx_reel_stop():
    """Reel settle: a cushioned wooden tick. Was a 120Hz thump — a drawer slamming."""
    n = int(0.18 * SR)
    x = np.zeros(n)
    mix_into(x, 0, mallet(note("A3"), 0.16, tone=0.3), 0.75)
    mix_into(x, 0, body_hit(150, 0.1, drop=0.35), 0.22)
    return fade_io(norm(widen(x, 0.001), 0.46))


# Scatters climb the pentatonic scale — the ESCALATION the operator liked, but the
# voice is now a pure crystal bell. The old version stacked a 110Hz thump under each
# ping, which is what made it read as a clank.
SCATTER_NOTES = ["A4", "C5", "E5", "A5", "C6"]


def sfx_scatter_stop(i):
    nn = SCATTER_NOTES[i]
    dur = 1.15 + i * 0.06
    x = bell(note(nn), dur, bright=0.78 + i * 0.05, warmth=1.0) * 1.0
    # a quiet perfect-fifth companion thickens each step without adding attack
    mix_into(x, int(0.006 * SR), bell(note(nn) * 1.5, dur * 0.7, bright=0.6, warmth=0.9), 0.22)
    mix_into(x, int(0.01 * SR), shimmer(0.45, density=5 + i * 2, f_lo=note(nn) * 2, f_hi=note(nn) * 6), 0.16)
    out = reverb(widen(x, 0.0022), mix=0.26, size=1.0, damp=5200)
    return fade_io(norm(out, 0.6 + i * 0.03))


def sfx_dragon_glide():
    """THE GLIDE — a LOOPING bed of moving air, played for exactly as long as the
    dragon is travelling (started at launch, stopped the moment it clears the board).
    A one-shot could not match a flight whose length varies with path length, and the
    one-shot player skips a retrigger while the same cue is still sounding — which is
    why it sometimes never fired at all when dragons launched back to back."""
    total = 0.9
    n = int(total * SR)
    tt = np.linspace(0, 1, n, endpoint=False)
    src = RNG.standard_normal(n)
    # slow undulation of the band centre so the loop breathes instead of droning
    centre = 300 * (1 + 0.55 * np.sin(2 * np.pi * tt))
    out = np.zeros(n)
    for c in np.geomspace(120, 1100, 6):
        w = np.exp(-((np.log(centre / c)) ** 2) / (2 * 0.6 ** 2))
        out += bandpass(src, c * 0.55, c * 1.8, order=2) * w
    out += lowpass(src, 200) * 0.6          # deep body
    out = lowpass(out, 1900)
    out *= 0.85 + 0.15 * np.sin(2 * np.pi * tt)   # gentle amplitude motion
    out = reverb(widen(out, 0.005), mix=0.22, size=1.1, damp=3600)
    return norm(fold_loop(out, total), 0.34)


def sfx_dragon_land():
    """DRAGON TOUCHES DOWN — a bright, high CHIME chord. Distinct from the path
    ignition below: this is the arrival, light and anticipatory, no body weight at
    all. (Both moments used to share one cue, which is why the land and the glide
    blurred into each other.)"""
    n = int(0.75 * SR)
    x = np.zeros(n)
    # open fifths/octaves high in the register — unambiguously a chime
    chord(x, 0, ["A5", "E6", "A6"], 0.7, gain=0.46, spread=0.014, bright=1.0, warmth=0.75)
    mix_into(x, int(0.05 * SR), bell(note("C7"), 0.45, bright=0.9, warmth=0.6), 0.16)
    mix_into(x, int(0.01 * SR), shimmer(0.4, density=6, f_lo=note("A6"), f_hi=note("A7")), 0.14)
    out = reverb(widen(x, 0.0022), mix=0.28, size=0.95, damp=6500)
    return fade_io(norm(out, 0.5))


def sfx_multiplier_landing():
    """DRAGON LANDS — a small anticipatory LIFT, not an impact. A rolled major-add9
    chord rising into place with only a touch of body under it. The old cue was a
    70Hz boom plus lowpassed noise: a struck pan."""
    n = int(0.85 * SR)
    x = np.zeros(n)
    chord(x, 0, ["A4", "E5", "B5"], 0.8, gain=0.5, spread=0.022, bright=0.8, warmth=1.0)
    # the "and there's more" tail — a fifth above, arriving a beat later, quieter
    mix_into(x, int(0.1 * SR), bell(note("E6"), 0.6, bright=0.7, warmth=0.9), 0.22)
    mix_into(x, 0, body_hit(130, 0.2, drop=0.35, warm=1.2), 0.28)
    mix_into(x, int(0.02 * SR), shimmer(0.5, density=7, f_lo=note("A5"), f_hi=note("A6")), 0.14)
    out = reverb(widen(x, 0.0025), mix=0.26, size=1.05, damp=5000)
    return fade_io(norm(out, 0.62))


def sfx_wild_explode():
    """Path ignition: a bright crystal bloom. Tuned partials instead of a noise burst."""
    n = int(0.9 * SR)
    x = np.zeros(n)
    chord(x, 0, ["A5", "C6", "E6", "A6"], 0.75, gain=0.34, spread=0.016, bright=0.95, warmth=0.95)
    mix_into(x, 0, shimmer(0.7, density=16, f_lo=2600, f_hi=8000), 0.3)
    mix_into(x, 0, whoosh(0.3, 1800, 5200, back=0.9), 0.16)
    mix_into(x, 0, body_hit(140, 0.18, drop=0.4), 0.22)
    out = reverb(widen(x, 0.003), mix=0.28, size=1.1)
    return fade_io(norm(out, 0.66))


def sfx_anticipation():
    """Loopable tension (2.4s): a breathing minor pad with a slow airy rise."""
    total = 2.4
    tt = t_axis(total)
    trem = 0.84 + 0.16 * np.sin(2 * np.pi * 5.0 * tt)
    x = np.zeros(len(tt))
    for nn, a in (("A3", 1.0), ("E4", 0.7), ("A4", 0.5), ("C5", 0.4)):
        x += (sine(note(nn) * 0.999, total) + sine(note(nn) * 1.001, total)) * a
    x = lowpass(x, 2000) * trem * 0.2
    x += whoosh(total, 700, 2000, curve=1.4, back=0.9) * 0.1
    x += sine(note("A2"), total) * 0.2
    out = reverb(widen(x, 0.004), mix=0.32, size=1.3)
    return norm(fold_loop(out, total), 0.42)


def sfx_bigwin_coinloop():
    """THE COUNT-UP (2.8s loop). This is the cue the operator called 'the inner
    workings of a computer' — it was a dense cloud of RANDOM-frequency impulses,
    i.e. band-limited static. It is now a MUSICAL figure: soft mallets running a
    pentatonic pattern in steady sixteenths, so a long count reads as coins piling
    up in tune rather than a machine chattering."""
    total = 2.8
    n = int(total * SR)
    x = np.zeros(n)
    step = total / 16
    # a rising pentatonic run that turns over cleanly at the loop point
    seq = ["A5", "C6", "E6", "C6", "A5", "E5", "A5", "C6",
           "E6", "G6", "E6", "C6", "A5", "C6", "E6", "A6"]
    for i, nn in enumerate(seq):
        g = 0.55 if i % 4 == 0 else 0.34
        mix_into(x, int(i * step * SR), mallet(note(nn), 0.26, tone=0.5), g)
    # a soft pad underneath keeps it from feeling like a music box on its own
    for nn in ("A3", "E4"):
        x += sine(note(nn), total) * 0.05
    mix_into(x, 0, shimmer(total, density=4, f_lo=3000, f_hi=7000), 0.12)
    out = reverb(widen(x, 0.0025), mix=0.24, size=0.95, damp=6000)
    return norm(fold_loop(out, total), 0.4)


def sfx_winlevel_small():
    """Per-line win: a two-note lift. Small, quick, must survive many repeats."""
    n = int(0.45 * SR)
    x = np.zeros(n)
    mix_into(x, 0, mallet(note("E5"), 0.3, tone=0.5), 0.7)
    mix_into(x, int(0.055 * SR), mallet(note("A5"), 0.34, tone=0.55), 0.75)
    out = reverb(widen(x, 0.0018), mix=0.2, size=0.85)
    return fade_io(norm(out, 0.46))


def sfx_winlevel_end():
    """Win presentation resolve: a settled perfect cadence."""
    n = int(1.4 * SR)
    x = np.zeros(n)
    chord(x, 0, ["E5", "A5", "C6"], 1.2, gain=0.4, spread=0.02, bright=0.8)
    mix_into(x, int(0.16 * SR), bell(note("A4"), 1.1, bright=0.7), 0.34)
    mix_into(x, 0, shimmer(0.7, density=8, f_lo=2200, f_hi=6000), 0.16)
    out = reverb(widen(x, 0.0025), mix=0.28, size=1.05)
    return fade_io(norm(out, 0.56))


def sfx_tier_up():
    """WIN TIER RANK-UP — the box promotes itself mid-count (BIG -> SUPER -> ...).
    A fast two-note upward hand-off landing on the tonic an octave up, with a short
    shimmer flick. Must read as PROMOTION over the win bgm + coin loop: quick, bright,
    no body, done in well under a second so back-to-back crossings never smear."""
    n = int(0.8 * SR)
    x = np.zeros(n)
    mix_into(x, 0, bell(note("E5"), 0.45, bright=0.9, warmth=0.8), 0.4)
    mix_into(x, int(0.075 * SR), bell(note("A5"), 0.6, bright=1.0, warmth=0.8), 0.62)
    mix_into(x, int(0.075 * SR), bell(note("E6"), 0.5, bright=0.9, warmth=0.7), 0.2)
    mix_into(x, int(0.09 * SR), shimmer(0.4, density=7, f_lo=note("A5"), f_hi=note("A7")), 0.16)
    out = reverb(widen(x, 0.002), mix=0.24, size=0.95, damp=6000)
    return fade_io(norm(out, 0.55))


def sfx_near_miss():
    """SCATTER NEAR-MISS — anticipation ran, the third scatter never came. A quiet
    two-note descending exhale (down a major third, soft mallets, no shimmer, short
    tail). Deliberately the DIMMEST cue in the kit: the decompression should register
    without ever feeling like a punishment sting."""
    n = int(0.7 * SR)
    x = np.zeros(n)
    mix_into(x, 0, mallet(note("E4"), 0.32, tone=0.4), 0.5)
    mix_into(x, int(0.17 * SR), mallet(note("C4"), 0.42, tone=0.35), 0.44)
    out = reverb(widen(x, 0.0015), mix=0.18, size=0.85, damp=3200)
    return fade_io(norm(out, 0.34))


def sfx_scatter_win():
    """Free spins triggered: an ascending crystal fanfare that lands on the tonic."""
    n = int(1.8 * SR)
    x = np.zeros(n)
    for i, nn in enumerate(("A4", "C5", "E5", "A5")):
        mix_into(x, int(i * 0.1 * SR), bell(note(nn), 1.1, bright=0.85), 0.5 + i * 0.06)
    chord(x, int(0.4 * SR), ["A5", "C6", "E6"], 1.2, gain=0.4, spread=0.02, bright=0.9)
    mix_into(x, int(0.4 * SR), shimmer(1.0, density=14, f_lo=2400, f_hi=7000), 0.24)
    mix_into(x, int(0.4 * SR), body_hit(110, 0.26, drop=0.4), 0.3)
    out = reverb(widen(x, 0.003), mix=0.3, size=1.15)
    return fade_io(norm(out, 0.68))


def sfx_superfreespin():
    """The transition INTO free spins: air rising, then the world opens up."""
    n = int(3.0 * SR)
    x = np.zeros(n)
    rise_d = 1.55
    mix_into(x, 0, whoosh(rise_d, 260, 4200, curve=1.6, back=1.0), 0.42)
    tt = t_axis(rise_d)
    f = note("A3") * 2 ** (np.linspace(0, 1.6, len(tt)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    mix_into(x, 0, lowpass(np.sin(ph), 2400) * np.linspace(0.04, 0.3, len(tt)))
    i0 = int(rise_d * SR)
    mix_into(x, i0, body_hit(85, 0.5, drop=0.35), 0.75)
    chord(x, i0, ["A4", "C5", "E5", "A5"], 1.35, gain=0.4, spread=0.018, bright=0.95)
    mix_into(x, i0, shimmer(1.2, density=16, f_lo=2400, f_hi=8000), 0.26)
    out = reverb(widen(x, 0.003), mix=0.3, size=1.35)
    return fade_io(norm(out, 0.76))


def jng_intro_fs():
    """Free-spin intro jingle: a crystal run resolving onto an open chord."""
    n = int(2.2 * SR)
    x = np.zeros(n)
    run = ["A4", "C5", "E5", "A5", "C6"]
    for i, nn in enumerate(run):
        mix_into(x, int(i * 0.115 * SR), bell(note(nn), 0.95, bright=0.88), 0.5)
    i0 = int(len(run) * 0.115 * SR)
    chord(x, i0, ["A3", "E4", "A4", "C5", "E5"], 1.4, gain=0.34, spread=0.022, bright=0.8)
    mix_into(x, i0, body_hit(90, 0.4, drop=0.4), 0.42)
    mix_into(x, i0, shimmer(1.0, density=12, f_lo=2200, f_hi=6500), 0.2)
    out = reverb(widen(x, 0.0025), mix=0.3, size=1.2)
    return fade_io(norm(out, 0.7))


def sfx_youwon_panel():
    """Feature total: a three-step cadence that keeps lifting (IV - V - I)."""
    n = int(2.0 * SR)
    x = np.zeros(n)
    steps = [(0.0, ["F4", "A4", "C5"]), (0.3, ["G4", "B4", "D5"]), (0.6, ["C5", "E5", "G5", "C6"])]
    for tm, ch in steps:
        chord(x, int(tm * SR), ch, 1.25, gain=0.36, spread=0.016, bright=0.85)
    mix_into(x, int(0.6 * SR), shimmer(1.0, density=12, f_lo=2000, f_hi=6500), 0.2)
    mix_into(x, 0, body_hit(95, 0.32, drop=0.42), 0.34)
    out = reverb(widen(x, 0.003), mix=0.3, size=1.2)
    return fade_io(norm(out, 0.72))


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
    "sfx_dragon_glide": (sfx_dragon_glide, True, 0.5),
    "sfx_dragon_land": (sfx_dragon_land, False, 0.62),
    "sfx_multiplier_landing": (sfx_multiplier_landing, False, 0.9),
    "sfx_near_miss": (sfx_near_miss, False, 0.5),
    "sfx_reel_stop_1": (sfx_reel_stop, False, 0.7),
    "sfx_scatter_stop_1": (lambda: sfx_scatter_stop(0), False, 0.75),
    "sfx_scatter_stop_2": (lambda: sfx_scatter_stop(1), False, 0.75),
    "sfx_scatter_stop_3": (lambda: sfx_scatter_stop(2), False, 0.78),
    "sfx_scatter_stop_4": (lambda: sfx_scatter_stop(3), False, 0.8),
    "sfx_scatter_stop_5": (lambda: sfx_scatter_stop(4), False, 0.82),
    "sfx_scatter_win_v2": (sfx_scatter_win, False, 0.8),
    "sfx_superfreespin": (sfx_superfreespin, False, 0.85),
    "sfx_tier_up": (sfx_tier_up, False, 0.75),
    "sfx_wild_explode": (sfx_wild_explode, False, 0.8),
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
