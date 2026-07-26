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

# Inharmonic partial ratios of a struck glass/crystal bar.
GLASS_PARTIALS = [(1.0, 1.0), (2.32, 0.45), (3.83, 0.28), (5.11, 0.14), (6.71, 0.08)]


def glass_bell(freq, dur=1.2, bright=1.0, strike=1.0):
    """Struck crystal: inharmonic partials + FM shimmer + strike chiff."""
    n = int(dur * SR)
    out = np.zeros(n)
    for i, (ratio, amp) in enumerate(GLASS_PARTIALS):
        f = freq * ratio
        if f > SR * 0.45:
            continue
        dec = dur * (0.9 / (1 + i * 0.8))
        detune = 1 + RNG.uniform(-0.0008, 0.0008)
        p = sine(f * detune, dur) * exp_env(dur, dec) * amp * (bright ** i)
        out += p
    # FM sparkle transient
    mod = sine(freq * 3.5, dur) * np.exp(-t_axis(dur) * 24) * 6
    out += np.sin(2 * np.pi * freq * 2.0 * t_axis(dur) + mod) * exp_env(dur, dur * 0.25) * 0.22 * bright
    # strike chiff
    chiff = highpass(RNG.standard_normal(n), freq * 2) * exp_env(dur, 0.012) * 0.5 * strike
    out += chiff
    return out * exp_env(dur, dur * 0.95)


def pluck(freq, dur=0.5, tone=2600.0):
    """Soft chime-pluck for arpeggios: detuned pair through a closing lowpass."""
    n = int(dur * SR)
    tt = t_axis(dur)
    raw = (np.sin(2 * np.pi * freq * 0.999 * tt) + np.sin(2 * np.pi * freq * 1.001 * tt)
           + 0.35 * np.sin(2 * np.pi * freq * 2 * tt) + 0.12 * np.sin(2 * np.pi * freq * 3 * tt))
    x = raw * exp_env(dur, dur * 0.55)
    x = lowpass(x, tone)
    x += highpass(RNG.standard_normal(n), 3000) * exp_env(dur, 0.006) * 0.12
    return x


def pad_note(freq, dur, tone=1400.0):
    """Dreamy pad partial: detuned triads of sines, slow attack."""
    tt = t_axis(dur)
    x = np.zeros(len(tt))
    for det in (0.996, 1.0, 1.004):
        for h, a in ((1, 1.0), (2, 0.35), (3, 0.12)):
            x += np.sin(2 * np.pi * freq * det * h * tt + RNG.uniform(0, 6.28)) * a
    x = lowpass(x, tone)
    return x * adsr(dur, a=min(0.6, dur * 0.3), d=0.2, s=0.8, r=min(0.8, dur * 0.3))


def sub_note(freq, dur):
    x = sine(freq, dur) + 0.15 * sine(freq * 2, dur)
    return soft_limit(x, 1.4) * adsr(dur, a=0.02, d=0.1, s=0.85, r=min(0.4, dur * 0.25))


def thump(freq=95.0, dur=0.35, drop=0.5):
    """Pitch-dropping sine knock (felt mallet)."""
    tt = t_axis(dur)
    f = freq * (drop + (1 - drop) * np.exp(-tt * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * exp_env(dur, dur * 0.5)
    x += lowpass(RNG.standard_normal(len(tt)), 900) * exp_env(dur, 0.02) * 0.4
    return x


def glitter(dur, density=28.0, f_lo=1800.0, f_hi=7500.0, decay_each=0.18):
    """A sparkling cloud of micro glass pings."""
    n = int(dur * SR)
    out = np.zeros(n + int(0.4 * SR))
    count = max(1, int(dur * density))
    times = np.sort(RNG.uniform(0, dur, count))
    for tm in times:
        f = np.exp(RNG.uniform(np.log(f_lo), np.log(f_hi)))
        d = RNG.uniform(0.06, decay_each)
        seg = sine(f, d) * exp_env(d, d) * RNG.uniform(0.3, 1.0)
        i0 = int(tm * SR)
        out[i0:i0 + len(seg)] += seg
    return out[:n + int(0.4 * SR)]


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

def sfx_btn_general():
    x = glass_bell(note("E6"), 0.16, bright=0.55, strike=0.9) * 0.7
    mix_into(x, 0, thump(420, 0.05, drop=0.7), 0.25)
    return fade_io(norm(widen(x, 0.001), 0.5))


def sfx_btn_spin():
    n = int(0.42 * SR)
    x = np.zeros(n)
    mix_into(x, 0, thump(150, 0.3, drop=0.55), 0.9)
    mix_into(x, int(0.02 * SR), sweep_noise(0.34, 500, 3400, bw=0.7) * exp_env(0.34, 0.3), 0.5)
    mix_into(x, int(0.05 * SR), glass_bell(note("A5"), 0.3, bright=0.7, strike=0.5), 0.35)
    return fade_io(norm(widen(x, 0.002), 0.72))


def sfx_reel_stop():
    n = int(0.24 * SR)
    x = np.zeros(n)
    mix_into(x, 0, thump(120, 0.2, drop=0.5))
    mix_into(x, int(0.004 * SR), glass_bell(note("C6"), 0.12, bright=0.5, strike=0.8), 0.22)
    return fade_io(norm(widen(x, 0.0015), 0.66))


SCATTER_NOTES = ["C5", "E5", "G5", "A5", "C6"]


def sfx_scatter_stop(i):
    nn = SCATTER_NOTES[i]
    x = glass_bell(note(nn), 0.95, bright=0.85 + i * 0.05, strike=0.6)
    mix_into(x, 0, glitter(0.4, density=10 + i * 5, f_lo=note(nn) * 2, f_hi=note(nn) * 5), 0.2)
    mix_into(x, 0, thump(110, 0.18, drop=0.55), 0.5)
    out = reverb(widen(x, 0.002), mix=0.22, size=0.9)
    return fade_io(norm(out, 0.7 + i * 0.02))


def sfx_multiplier_landing():
    """Dragon slam: weighty boom + crystal ring."""
    n = int(0.8 * SR)
    x = np.zeros(n)
    mix_into(x, 0, thump(70, 0.5, drop=0.4), 1.3)
    mix_into(x, 0, lowpass(RNG.standard_normal(int(0.5 * SR)), 160) * exp_env(0.5, 0.35), 0.5)
    mix_into(x, int(0.015 * SR), glass_bell(note("A4"), 0.7, bright=0.95, strike=0.4), 0.5)
    mix_into(x, int(0.015 * SR), glass_bell(note("E5"), 0.6, bright=0.9, strike=0.2), 0.3)
    out = reverb(widen(x, 0.002), mix=0.2, size=1.0, damp=3800)
    return fade_io(norm(out, 0.85))


def sfx_wild_explode():
    """Crystalline shatter burst."""
    n = int(0.95 * SR)
    x = np.zeros(n)
    mix_into(x, 0, highpass(RNG.standard_normal(int(0.25 * SR)), 2200) * exp_env(0.25, 0.05), 0.8)
    cluster = [note("C6"), note("E6"), note("G6"), note("B6")]
    for i, f in enumerate(cluster):
        b = glass_bell(f * RNG.uniform(0.99, 1.01), 0.7, bright=1.0, strike=0.3)
        mix_into(x, int((0.01 + i * 0.015) * SR), b, 0.35)
    mix_into(x, 0, glitter(0.6, density=40, f_lo=2500, f_hi=9000), 0.4)
    mix_into(x, 0, thump(140, 0.25, drop=0.5), 0.5)
    out = reverb(widen(x, 0.003), mix=0.24, size=1.0)
    return fade_io(norm(out, 0.8))


def sfx_anticipation():
    """Loopable tension shimmer (2.4s): tremolo minor pad + slow rising air."""
    total = 2.4
    tt = t_axis(total)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 7 * tt)
    x = np.zeros(len(tt))
    for nn, a in (("A4", 1.0), ("C5", 0.8), ("E5", 0.6), ("A5", 0.35)):
        x += (sine(note(nn) * 0.999, total) + sine(note(nn) * 1.001, total)) * a
    x = lowpass(x, 2600) * trem * 0.22
    x += sweep_noise(total, 1200, 2600, bw=0.35) * 0.18
    x += sine(note("A2"), total) * 0.25
    out = reverb(widen(x, 0.004), mix=0.3, size=1.3)
    return norm(fold_loop(out, total), 0.5)


def sfx_bigwin_coinloop():
    """Loopable crystal-coin cascade (2.8s)."""
    total = 2.8
    x = glitter(total, density=34, f_lo=2000, f_hi=8200, decay_each=0.22)
    x += glitter(total, density=12, f_lo=900, f_hi=2100, decay_each=0.3) * 0.7
    out = reverb(widen(x, 0.003), mix=0.2, size=0.9)
    return norm(fold_loop(out, total), 0.55)


def sfx_winlevel_small():
    """Per-line win chime: quick 3-note glass arp (light, non-fatiguing)."""
    n = int(0.55 * SR)
    x = np.zeros(n)
    for i, nn in enumerate(("C5", "E5", "G5")):
        mix_into(x, int(i * 0.05 * SR), pluck(note(nn), 0.4, tone=3400), 0.8)
    out = reverb(widen(x, 0.002), mix=0.18, size=0.8)
    return fade_io(norm(out, 0.62))


def sfx_winlevel_end():
    n = int(1.3 * SR)
    x = np.zeros(n)
    for i, (nn, g) in enumerate((("G5", 0.8), ("C5", 1.0))):
        mix_into(x, int(i * 0.14 * SR), glass_bell(note(nn), 1.0, bright=0.8, strike=0.4), g)
    mix_into(x, 0, glitter(0.7, density=14, f_lo=1500, f_hi=5000), 0.25)
    out = reverb(widen(x, 0.002), mix=0.25, size=1.0)
    return fade_io(norm(out, 0.66))


def sfx_scatter_win():
    """Scatter celebration on free-spin trigger."""
    n = int(1.7 * SR)
    x = np.zeros(n)
    for i, nn in enumerate(("C5", "E5", "G5", "C6", "E6")):
        b = glass_bell(note(nn), 1.1, bright=0.95, strike=0.5)
        mix_into(x, int(i * 0.09 * SR), b, 0.7 + i * 0.06)
    mix_into(x, 0, glitter(1.1, density=26, f_lo=2000, f_hi=7000), 0.35)
    mix_into(x, 0, thump(100, 0.3, drop=0.5), 0.4)
    out = reverb(widen(x, 0.003), mix=0.26, size=1.1)
    return fade_io(norm(out, 0.75))


def sfx_superfreespin():
    """Riser into impact — the transition INTO free spins."""
    n = int(3.0 * SR)
    x = np.zeros(n)
    rise = sweep_noise(1.6, 300, 5200, bw=0.6) * np.linspace(0.15, 1.0, int(1.6 * SR))
    mix_into(x, 0, rise, 0.5)
    tt = t_axis(1.6)
    f = 220 * 2 ** (tt / 1.6 * 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    mix_into(x, 0, np.sin(ph) * np.linspace(0.05, 0.4, len(tt)))
    i0 = int(1.6 * SR)
    mix_into(x, i0, thump(75, 0.6, drop=0.4), 1.2)
    chord = [note("A4"), note("C5"), note("E5"), note("A5")]
    for f2 in chord:
        mix_into(x, i0, glass_bell(f2, 1.3, bright=1.0, strike=0.3), 0.4)
    mix_into(x, i0, glitter(1.2, density=24, f_lo=2000, f_hi=8000), 0.35)
    out = reverb(widen(x, 0.003), mix=0.28, size=1.3)
    return fade_io(norm(out, 0.85))


def jng_intro_fs():
    """Free-spin intro jingle: ascending crystal run + resolve."""
    bpm = 110
    beat = 60 / bpm
    n = int(2.1 * SR)
    x = np.zeros(n)
    run = ["A4", "C5", "E5", "G5", "A5", "C6"]
    for i, nn in enumerate(run):
        mix_into(x, int(i * 0.25 * beat * SR), glass_bell(note(nn), 0.9, bright=0.9, strike=0.5), 0.55)
    i0 = int(len(run) * 0.25 * beat * SR)
    for nn in ("A3", "E4", "A4", "C5", "E5"):
        mix_into(x, i0, glass_bell(note(nn), 1.3, bright=0.85, strike=0.35), 0.4)
    mix_into(x, i0, thump(85, 0.4, drop=0.45), 0.7)
    out = reverb(widen(x, 0.002), mix=0.26, size=1.15)
    return fade_io(norm(out, 0.78))


def sfx_youwon_panel():
    """Feature-total panel: triumphant cadence."""
    n = int(1.9 * SR)
    x = np.zeros(n)
    steps = [(0.0, ["C4", "E4", "G4"]), (0.28, ["F4", "A4", "C5"]), (0.56, ["C5", "E5", "G5", "C6"])]
    for tm, chord in steps:
        for nn in chord:
            mix_into(x, int(tm * SR), glass_bell(note(nn), 1.2, bright=0.9, strike=0.4), 0.4)
    mix_into(x, int(0.56 * SR), glitter(1.0, density=20, f_lo=1800, f_hi=6500), 0.3)
    mix_into(x, 0, thump(90, 0.35, drop=0.5), 0.5)
    out = reverb(widen(x, 0.003), mix=0.28, size=1.15)
    return fade_io(norm(out, 0.8))


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
    "sfx_multiplier_landing": (sfx_multiplier_landing, False, 0.9),
    "sfx_reel_stop_1": (sfx_reel_stop, False, 0.7),
    "sfx_scatter_stop_1": (lambda: sfx_scatter_stop(0), False, 0.75),
    "sfx_scatter_stop_2": (lambda: sfx_scatter_stop(1), False, 0.75),
    "sfx_scatter_stop_3": (lambda: sfx_scatter_stop(2), False, 0.78),
    "sfx_scatter_stop_4": (lambda: sfx_scatter_stop(3), False, 0.8),
    "sfx_scatter_stop_5": (lambda: sfx_scatter_stop(4), False, 0.82),
    "sfx_scatter_win_v2": (sfx_scatter_win, False, 0.8),
    "sfx_superfreespin": (sfx_superfreespin, False, 0.85),
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
