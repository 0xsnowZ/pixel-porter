#!/usr/bin/env python3
"""
Pixel Porter - High-Quality Procedural Lo-Fi & Industrial BGM Composer
Generates 2 lightweight, seamless looping background music tracks:
1. assets/audio/bgm_lofi_shift.ogg (Lo-Fi Warehouse Shift - Relaxed chill study beats)
2. assets/audio/bgm_industrial_pulse.ogg (Industrial Pulse - Focused ambient warehouse synth)
"""

import os
import math
import wave
import subprocess
import numpy as np

SAMPLE_RATE = 44100
ASSETS_AUDIO_DIR = "/home/snowz/godot/assets/audio"
os.makedirs(ASSETS_AUDIO_DIR, exist_ok=True)


def adsr(length, a=0.01, d=0.1, s=0.7, r=0.2):
    """Generates an ADSR envelope of given sample length."""
    na = int(length * a)
    nd = int(length * d)
    nr = int(length * r)
    ns = length - na - nd - nr
    if ns < 0:
        ns = 0
        scale = length / max(1, (na + nd + nr))
        na = int(na * scale)
        nd = int(nd * scale)
        nr = length - na - nd
    env = np.zeros(length, dtype=np.float32)
    if na > 0:
        env[:na] = np.linspace(0.0, 1.0, na)
    if nd > 0:
        env[na:na+nd] = np.linspace(1.0, s, nd)
    if ns > 0:
        env[na+nd:na+nd+ns] = s
    if nr > 0:
        env[na+nd+ns:] = np.linspace(s, 0.0, nr)
    return env


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def apply_stereo_reverb(left, right, sr=SAMPLE_RATE, room_size=0.6, damping=0.3):
    """Simple high-performance stereo comb/allpass delay feedback reverb."""
    delays_l = [int(sr * d) for d in [0.029, 0.037, 0.043, 0.053]]
    delays_r = [int(sr * d) for d in [0.031, 0.041, 0.047, 0.059]]
    out_l = np.copy(left)
    out_r = np.copy(right)
    for dl in delays_l:
        comb = np.zeros_like(left)
        for i in range(dl, len(left)):
            comb[i] = left[i - dl] + comb[i - dl] * room_size * (1.0 - damping)
        out_l += comb * 0.15
    for dr in delays_r:
        comb = np.zeros_like(right)
        for i in range(dr, len(right)):
            comb[i] = right[i - dr] + comb[i - dr] * room_size * (1.0 - damping)
        out_r += comb * 0.15
    return out_l, out_r


def make_seamless_loop(audio_stereo, loop_samples, tail_samples):
    """Wraps the tail over the start so the loop has zero cut in reverb/sound."""
    main = audio_stereo[:, :loop_samples].copy()
    tail = audio_stereo[:, loop_samples:loop_samples + tail_samples]
    wrap_len = min(tail.shape[1], main.shape[1])
    main[:, :wrap_len] += tail[:, :wrap_len]
    return main


# ==============================================================================
# TRACK 1: "Lo-Fi Warehouse Shift" (Tempo 78 BPM, 16 Bars)
# ==============================================================================

def generate_lofi_track():
    bpm = 78.0
    sr = SAMPLE_RATE
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0
    total_bars = 16
    loop_samples = int(total_bars * bar_dur * sr)
    tail_samples = int(3.0 * sr) # 3 seconds tail
    total_samples = loop_samples + tail_samples

    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    chord_seq = [
        # Bar 0-3
        ([50, 57, 60, 64, 69], 38), # Dm9, bass D2
        ([43, 55, 59, 64, 67], 43), # G13, bass G2
        ([48, 55, 59, 62, 67], 36), # Cmaj9, bass C2
        ([45, 52, 55, 60, 64], 45), # Am9, bass A2
        # Bar 4-7
        ([50, 57, 60, 64, 69], 38),
        ([43, 55, 59, 64, 67], 43),
        ([48, 55, 59, 62, 67], 36),
        ([45, 52, 55, 60, 64], 45),
        # Bar 8-11
        ([53, 57, 60, 64, 67], 41), # Fmaj7, bass F2
        ([52, 55, 59, 62, 67], 40), # Em7, bass E2
        ([50, 57, 60, 64, 69], 38), # Dm9, bass D2
        ([43, 53, 56, 59, 65], 43), # G7b9, bass G2
        # Bar 12-15
        ([50, 57, 60, 64, 69], 38),
        ([43, 55, 59, 64, 67], 43),
        ([48, 55, 59, 62, 67], 36),
        ([45, 52, 55, 60, 64], 45),
    ]

    # 1. Synthesize Rhodes / Electric Piano Chords
    for bar_idx, (chord, bass_note) in enumerate(chord_seq):
        start_time = bar_idx * bar_dur
        start_idx = int(start_time * sr)
        chord_len = int(bar_dur * 0.95 * sr)
        t = np.linspace(0, bar_dur * 0.95, chord_len, False)
        env = adsr(chord_len, a=0.03, d=0.25, s=0.45, r=0.35)

        chord_wave_l = np.zeros(chord_len, dtype=np.float32)
        chord_wave_r = np.zeros(chord_len, dtype=np.float32)

        # Tremolo
        tremolo_l = 1.0 + 0.18 * np.sin(2.0 * np.pi * 3.5 * t)
        tremolo_r = 1.0 + 0.18 * np.sin(2.0 * np.pi * 3.5 * t + math.pi * 0.5)

        for note in chord:
            freq = midi_to_freq(note)
            w = (np.sin(2 * np.pi * freq * t) +
                 0.35 * np.sin(2 * np.pi * freq * 2 * t) +
                 0.12 * np.sin(2 * np.pi * freq * 3 * t))
            pan = 0.5 + 0.2 * np.sin(note)
            chord_wave_l += w * (1.0 - pan)
            chord_wave_r += w * pan

        chord_wave_l = chord_wave_l * env * tremolo_l * 0.08
        chord_wave_r = chord_wave_r * env * tremolo_r * 0.08

        left[start_idx:start_idx + chord_len] += chord_wave_l
        right[start_idx:start_idx + chord_len] += chord_wave_r

        # 2. Warm Sub Bass
        for beat_offset in [0.0, 2.0]:
            b_start = int((start_time + beat_offset * beat_dur) * sr)
            b_len = int(beat_dur * 1.8 * sr)
            bt = np.linspace(0, beat_dur * 1.8, b_len, False)
            bfreq = midi_to_freq(bass_note)
            benv = adsr(b_len, a=0.04, d=0.3, s=0.6, r=0.2)
            bwave = np.sin(2 * np.pi * bfreq * bt) + 0.25 * np.sin(2 * np.pi * bfreq * 2 * bt)
            bwave = np.tanh(bwave * 1.5) * benv * 0.18
            left[b_start:b_start + b_len] += bwave * 0.5
            right[b_start:b_start + b_len] += bwave * 0.5

    # 3. Lo-Fi Drums (Kick, Snare/Rim, Hi-Hat)
    for bar_idx in range(total_bars):
        bar_start = bar_idx * bar_dur
        for k_beat in [0.0, 2.5]:
            k_time = bar_start + k_beat * beat_dur
            k_idx = int(k_time * sr)
            k_len = int(0.28 * sr)
            kt = np.linspace(0, 0.28, k_len, False)
            k_pitch = 120.0 * np.exp(-18.0 * kt) + 48.0
            k_phase = 2.0 * np.pi * np.cumsum(k_pitch) / sr
            kwave = np.sin(k_phase) * np.exp(-12.0 * kt) * 0.24
            left[k_idx:k_idx + k_len] += kwave
            right[k_idx:k_idx + k_len] += kwave

        for s_beat in [1.0, 3.0]:
            s_time = bar_start + s_beat * beat_dur
            s_idx = int(s_time * sr)
            s_len = int(0.20 * sr)
            st = np.linspace(0, 0.20, s_len, False)
            noise = np.random.uniform(-1.0, 1.0, s_len).astype(np.float32)
            tone = np.sin(2 * np.pi * 220.0 * st)
            swave = (noise * 0.6 + tone * 0.4) * np.exp(-16.0 * st) * 0.15
            left[s_idx:s_idx + s_len] += swave
            right[s_idx:s_idx + s_len] += swave

        for h_step in range(8):
            h_time = bar_start + (h_step * 0.5 + (0.02 if h_step % 2 == 1 else 0.0)) * beat_dur
            h_idx = int(h_time * sr)
            h_len = int(0.06 * sr)
            ht = np.linspace(0, 0.06, h_len, False)
            h_noise = np.random.uniform(-1.0, 1.0, h_len).astype(np.float32)
            h_vol = 0.08 if h_step % 2 == 0 else 0.04
            hwave = h_noise * np.exp(-55.0 * ht) * h_vol
            left[h_idx:h_idx + h_len] += hwave * 0.4
            right[h_idx:h_idx + h_len] += hwave * 0.6

    # 4. Mellow Flute/Synth Melody
    lead_notes = [
        (4, 0.5, 1.5, 69), (4, 2.0, 1.0, 72), (4, 3.0, 1.0, 71),
        (5, 0.0, 2.0, 67), (5, 2.5, 1.5, 64),
        (6, 0.0, 1.5, 67), (6, 2.0, 1.0, 69), (6, 3.0, 1.0, 72),
        (7, 0.0, 3.0, 71),
        (8, 0.5, 1.5, 72), (8, 2.0, 1.0, 74), (8, 3.0, 1.0, 76),
        (9, 0.0, 2.0, 74), (9, 2.5, 1.5, 71),
        (10, 0.0, 1.5, 69), (10, 2.0, 1.0, 67), (10, 3.0, 1.0, 65),
        (11, 0.0, 3.0, 64),
    ]
    for bar_num, beat_num, dur_beats, midi_note in lead_notes:
        n_time = (bar_num * 4.0 + beat_num) * beat_dur
        n_idx = int(n_time * sr)
        n_len = int(dur_beats * beat_dur * sr)
        nt = np.linspace(0, dur_beats * beat_dur, n_len, False)
        freq = midi_to_freq(midi_note)
        vib = 1.0 + 0.006 * np.sin(2 * np.pi * 5.0 * nt)
        env = adsr(n_len, a=0.1, d=0.2, s=0.7, r=0.3)
        nwave = (np.sin(2 * np.pi * freq * vib * nt) + 0.2 * np.sin(2 * np.pi * freq * 2 * vib * nt)) * env * 0.07
        left[n_idx:n_idx + n_len] += nwave * 0.65
        right[n_idx:n_idx + n_len] += nwave * 0.35

    # 5. Vinyl Texture
    crackle = np.random.uniform(-0.015, 0.015, total_samples).astype(np.float32)
    left += crackle * 0.3
    right += crackle * 0.3

    # 6. Apply Stereo Reverb
    rev_l, rev_r = apply_stereo_reverb(left, right, sr=sr, room_size=0.55, damping=0.35)

    # 7. Make Seamless Loop
    stereo = np.vstack([rev_l, rev_r])
    looped_stereo = make_seamless_loop(stereo, loop_samples, tail_samples)

    peak = np.max(np.abs(looped_stereo))
    if peak > 0:
        looped_stereo = (looped_stereo / peak) * 0.88

    return looped_stereo, sr


# ==============================================================================
# TRACK 2: "Industrial Pulse" (Tempo 96 BPM, 16 Bars)
# ==============================================================================

def generate_industrial_track():
    bpm = 96.0
    sr = SAMPLE_RATE
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0
    total_bars = 16
    loop_samples = int(total_bars * bar_dur * sr)
    tail_samples = int(3.0 * sr)
    total_samples = loop_samples + tail_samples

    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    bass_pattern = [
        (40, 1.0), (40, 0.4), (52, 0.7), (40, 0.5),
        (40, 0.9), (40, 0.3), (43, 0.8), (40, 0.4),
        (40, 1.0), (40, 0.4), (55, 0.7), (40, 0.5),
        (45, 0.8), (43, 0.7), (42, 0.6), (40, 0.5)
    ]
    sixteenth_dur = beat_dur * 0.25

    for bar in range(total_bars):
        root_offset = 0
        if bar in [4, 5]:
            root_offset = 5 # Am
        elif bar in [8, 9]:
            root_offset = 8 # C
        elif bar in [10, 11]:
            root_offset = 7 # B

        for step, (note, vel) in enumerate(bass_pattern):
            t_start = (bar * bar_dur) + (step * sixteenth_dur)
            idx = int(t_start * sr)
            dur = sixteenth_dur * 0.85
            s_len = int(dur * sr)
            st = np.linspace(0, dur, s_len, False)
            freq = midi_to_freq(note + root_offset)
            env = adsr(s_len, a=0.01, d=0.15, s=0.3, r=0.2)
            saw = (2.0 * (freq * st - np.floor(0.5 + freq * st))) * 0.6
            sub = np.sin(2 * np.pi * freq * 0.5 * st) * 0.8
            b_wave = (saw + sub) * env * vel * 0.15
            b_wave = np.tanh(b_wave * 1.8)
            left[idx:idx + s_len] += b_wave
            right[idx:idx + s_len] += b_wave

    pad_len = loop_samples + tail_samples
    pad_t = np.linspace(0, (total_bars * bar_dur) + 3.0, pad_len, False)
    for p_midi in [40, 47, 52, 55, 59]:
        p_freq = midi_to_freq(p_midi)
        w1 = np.sin(2 * np.pi * p_freq * pad_t)
        w2 = np.sin(2 * np.pi * (p_freq * 1.003) * pad_t)
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * pad_t)
        p_wave = (w1 + w2) * 0.012 * lfo
        left += p_wave * 0.7
        right += p_wave * 0.5

    for bar in range(total_bars):
        for clink_beat in [1.5, 3.5, 2.75]:
            c_time = (bar * bar_dur) + (clink_beat * beat_dur)
            c_idx = int(c_time * sr)
            c_len = int(0.35 * sr)
            ct = np.linspace(0, 0.35, c_len, False)
            mod = np.sin(2 * np.pi * 820.0 * ct) * np.exp(-18.0 * ct) * 3.5
            carrier = np.sin(2 * np.pi * 1480.0 * ct + mod) * np.exp(-14.0 * ct)
            clink = carrier * 0.08
            pan = 0.3 if clink_beat == 1.5 else 0.7
            left[c_idx:c_idx + c_len] += clink * (1.0 - pan)
            right[c_idx:c_idx + c_len] += clink * pan

        for k_beat in [0.0, 1.0, 2.0, 3.0]:
            k_time = (bar * bar_dur) + (k_beat * beat_dur)
            k_idx = int(k_time * sr)
            k_len = int(0.22 * sr)
            kt = np.linspace(0, 0.22, k_len, False)
            k_pitch = 140.0 * np.exp(-24.0 * kt) + 42.0
            k_phase = 2.0 * np.pi * np.cumsum(k_pitch) / sr
            kwave = np.sin(k_phase) * np.exp(-10.0 * kt) * 0.22
            left[k_idx:k_idx + k_len] += kwave
            right[k_idx:k_idx + k_len] += kwave

        for s_step in range(16):
            if s_step % 2 == 1:
                h_time = (bar * bar_dur) + (s_step * sixteenth_dur)
                h_idx = int(h_time * sr)
                h_len = int(0.045 * sr)
                ht = np.linspace(0, 0.045, h_len, False)
                noise = np.random.uniform(-1.0, 1.0, h_len).astype(np.float32)
                hwave = noise * np.exp(-60.0 * ht) * (0.07 if s_step % 4 == 2 else 0.04)
                left[h_idx:h_idx + h_len] += hwave * 0.5
                right[h_idx:h_idx + h_len] += hwave * 0.5

    arp_notes = [64, 67, 71, 76, 74, 71, 67, 64]
    for bar in range(4, total_bars):
        for step in range(8):
            a_time = (bar * bar_dur) + (step * (bar_dur / 8.0))
            a_idx = int(a_time * sr)
            a_len = int((bar_dur / 8.0) * 0.75 * sr)
            at = np.linspace(0, (bar_dur / 8.0) * 0.75, a_len, False)
            midi = arp_notes[step % len(arp_notes)]
            freq = midi_to_freq(midi)
            env = adsr(a_len, a=0.01, d=0.2, s=0.2, r=0.2)
            awave = (np.sin(2 * np.pi * freq * at) + 0.3 * np.sin(2 * np.pi * freq * 2 * at)) * env * 0.06
            pan = 0.5 + 0.35 * np.sin(step * 0.8)
            left[a_idx:a_idx + a_len] += awave * (1.0 - pan)
            right[a_idx:a_idx + a_len] += awave * pan

    rev_l, rev_r = apply_stereo_reverb(left, right, sr=sr, room_size=0.6, damping=0.25)
    stereo = np.vstack([rev_l, rev_r])
    looped_stereo = make_seamless_loop(stereo, loop_samples, tail_samples)

    peak = np.max(np.abs(looped_stereo))
    if peak > 0:
        looped_stereo = (looped_stereo / peak) * 0.88

    return looped_stereo, sr


def export_audio_to_ogg(stereo_data, sr, base_filename):
    wav_path = f"/tmp/{base_filename}.wav"
    ogg_path = os.path.join(ASSETS_AUDIO_DIR, f"{base_filename}.ogg")

    int_data = (stereo_data * 32767.0).clip(-32768, 32767).astype(np.int16)
    interleaved = np.empty((int_data.shape[1] * 2,), dtype=np.int16)
    interleaved[0::2] = int_data[0]
    interleaved[1::2] = int_data[1]

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(interleaved.tobytes())

    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-c:a", "libvorbis", "-q:a", "4",
        ogg_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(wav_path):
        os.remove(wav_path)
    sz = os.path.getsize(ogg_path)
    print(f"Generated {ogg_path} ({sz / 1024:.1f} KB)")


if __name__ == "__main__":
    print("Synthesizing Lo-Fi Warehouse Shift...")
    lofi_audio, sr = generate_lofi_track()
    export_audio_to_ogg(lofi_audio, sr, "bgm_lofi_shift")

    print("Synthesizing Industrial Pulse...")
    ind_audio, sr = generate_industrial_track()
    export_audio_to_ogg(ind_audio, sr, "bgm_industrial_pulse")
    print("Done generating BGM tracks.")
