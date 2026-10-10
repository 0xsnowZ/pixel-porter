#!/usr/bin/env python3
"""
Pixel Porter - Studio-Grade Procedural BGM Generator
Generates 2 high-production, dynamic, non-fatiguing soundtrack pieces:
1. assets/audio/bgm_lofi_shift.ogg ("Warehouse Chill" - Mellow 74 BPM Lo-Fi study beats with Rhodes piano, upright bass, gentle brushed drums & atmospheric breathing space)
2. assets/audio/bgm_industrial_pulse.ogg ("Industrial Pulse" - Atmospheric 80 BPM Ambient Warehouse Soundscape with warm analog pads, kalimba bells & spacious reverb)
"""

import os
import math
import wave
import subprocess
import numpy as np

SAMPLE_RATE = 44100
ASSETS_AUDIO_DIR = "/home/snowz/godot/assets/audio"
os.makedirs(ASSETS_AUDIO_DIR, exist_ok=True)


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def apply_fast_stereo_reverb(left, right, sr=SAMPLE_RATE):
    """Fast vectorized multi-tap spatial delay."""
    delays_l = [int(sr * d) for d in [0.031, 0.043, 0.059, 0.073]]
    delays_r = [int(sr * d) for d in [0.037, 0.047, 0.061, 0.079]]
    gains = [0.18, 0.14, 0.10, 0.08]

    out_l = np.copy(left)
    out_r = np.copy(right)

    for dl, g in zip(delays_l, gains):
        if dl < len(left):
            tap = np.zeros_like(left)
            tap[dl:] = left[:-dl] * g
            out_l += tap

    for dr, g in zip(delays_r, gains):
        if dr < len(right):
            tap = np.zeros_like(right)
            tap[dr:] = right[:-dr] * g
            out_r += tap

    return out_l, out_r


def make_seamless_loop(audio_stereo, loop_samples, tail_samples):
    main = audio_stereo[:, :loop_samples].copy()
    tail = audio_stereo[:, loop_samples:loop_samples + tail_samples]
    wrap_len = min(tail.shape[1], main.shape[1])
    main[:, :wrap_len] += tail[:, :wrap_len]
    return main


# ==============================================================================
# TRACK 1: "Warehouse Chill" (Lo-Fi Study / Puzzle Beats - 32 Bars @ 74 BPM)
# ==============================================================================

def synth_rhodes_chord(chord_midi, duration_sec, sr=SAMPLE_RATE):
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, False)
    chord_l = np.zeros(n_samples, dtype=np.float32)
    chord_r = np.zeros(n_samples, dtype=np.float32)

    # Gentle stereo tremolo
    tremolo_l = 1.0 + 0.10 * np.sin(2.0 * np.pi * 3.6 * t)
    tremolo_r = 1.0 + 0.10 * np.sin(2.0 * np.pi * 3.6 * t + 0.5 * math.pi)

    for i, midi_val in enumerate(chord_midi):
        freq = midi_to_freq(midi_val)
        decay_1 = np.exp(-t / 2.2)
        decay_2 = np.exp(-t / 1.1)
        decay_3 = np.exp(-t / 0.55)
        decay_tine = np.exp(-t / 0.035)

        h1 = np.sin(2 * np.pi * freq * t) * decay_1
        h2 = 0.32 * np.sin(2 * np.pi * 2.0 * freq * t) * decay_2
        h3 = 0.10 * np.sin(2 * np.pi * 3.01 * freq * t) * decay_3
        tine = 0.05 * np.sin(2 * np.pi * 6.82 * freq * t) * decay_tine

        note_wave = (h1 + h2 + h3 + tine)
        pan = 0.5 + 0.28 * math.sin(i * 1.7)
        chord_l += note_wave * (1.0 - pan)
        chord_r += note_wave * pan

    # Soft tape saturation
    chord_l = np.tanh(chord_l * 0.42) * tremolo_l
    chord_r = np.tanh(chord_r * 0.42) * tremolo_r
    return chord_l, chord_r


def synth_warm_bass(midi_val, duration_sec, sr=SAMPLE_RATE):
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, False)
    freq = midi_to_freq(midi_val)
    attack = np.minimum(1.0, t / 0.02)
    decay = np.exp(-t / 1.8)
    env = attack * decay
    w1 = np.sin(2 * np.pi * freq * t)
    w2 = 0.20 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t / 0.8)
    return np.tanh((w1 + w2) * 1.2) * env * 0.28


def generate_lofi_track():
    bpm = 74.0
    sr = SAMPLE_RATE
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0
    total_bars = 32
    loop_samples = int(total_bars * bar_dur * sr)
    tail_samples = int(4.0 * sr)
    total_samples = loop_samples + tail_samples

    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    # 32-Bar Extended Neo-Soul / Lo-Fi Jazz Progression
    chord_seq = [
        # Part A (Bars 0-7): Cozy morning warehouse
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([43, 53, 59, 64, 67], 43),  # G13
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([45, 52, 55, 60, 64], 45),  # Am9
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([43, 53, 56, 59, 65], 43),  # G7(b9)
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([40, 52, 55, 59, 62], 40),  # Em7

        # Part B (Bars 8-15): Harmonic Elevation
        ([53, 57, 60, 64, 67], 41),  # Fmaj7
        ([52, 55, 59, 62, 67], 40),  # Em7
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([43, 53, 59, 64, 67], 43),  # G13
        ([53, 57, 60, 64, 67], 41),  # Fmaj7
        ([53, 56, 60, 62, 65], 41),  # Fm6
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([45, 52, 55, 61, 64], 45),  # A7(#9)

        # Part C (Bars 16-23): Variation with gentle counterpoint
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([43, 53, 59, 64, 67], 43),  # G13
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([45, 52, 55, 60, 64], 45),  # Am9
        ([46, 53, 57, 60, 65], 46),  # Bbmaj7
        ([45, 52, 55, 61, 65], 45),  # A7(b13)
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([43, 53, 55, 59, 65], 43),  # G7

        # Part D (Bars 24-31): Atmospheric Breather (Drums drop out, spacious chords)
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([50, 57, 60, 64, 69], 38),  # Dm9
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([53, 57, 60, 64, 67], 41),  # Fmaj7
        ([43, 53, 59, 64, 67], 43),  # G13
        ([48, 55, 59, 62, 67], 36),  # Cmaj9
        ([45, 52, 55, 61, 64], 45),  # A7(alt) -> Turnaround
    ]

    for bar_idx, (chord, bass_note) in enumerate(chord_seq):
        start_t = bar_idx * bar_dur
        start_idx = int(start_t * sr)

        # In breather bars 24-27, sustain chords longer and softer
        is_breather = (24 <= bar_idx <= 27)
        dur = bar_dur * (1.1 if is_breather else 0.95)
        cl, cr = synth_rhodes_chord(chord, dur, sr)
        gain = 0.11 if is_breather else 0.13
        end_idx = min(start_idx + len(cl), total_samples)
        left[start_idx:end_idx] += cl[:end_idx - start_idx] * gain
        right[start_idx:end_idx] += cr[:end_idx - start_idx] * gain

        # Bassline
        bass_offsets = [0.0] if is_breather else [0.0, 2.0]
        for boff in bass_offsets:
            bt_start = int((start_t + boff * beat_dur) * sr)
            b_dur = beat_dur * (2.8 if is_breather else 1.7)
            b_wave = synth_warm_bass(bass_note, b_dur, sr)
            bend = min(bt_start + len(b_wave), total_samples)
            left[bt_start:bend] += b_wave[:bend - bt_start] * 0.42
            right[bt_start:bend] += b_wave[:bend - bt_start] * 0.42

    # Lo-Fi Brushed Drums (Active in bars 0-23 and 28-31; DROPPED in breather 24-27!)
    for bar_idx in range(total_bars):
        if 24 <= bar_idx <= 27:
            continue # Acoustic breathing room!

        bar_start = bar_idx * bar_dur

        # Mellow pillowy kick on beat 0 and 2.5
        for k_beat in [0.0, 2.5]:
            kt = bar_start + k_beat * beat_dur
            k_idx = int(kt * sr)
            k_dur = 0.22
            k_len = int(k_dur * sr)
            t_k = np.linspace(0, k_dur, k_len, False)
            pitch = 65.0 * np.exp(-16.0 * t_k) + 40.0
            phase = 2.0 * np.pi * np.cumsum(pitch) / sr
            kwave = np.sin(phase) * np.exp(-11.0 * t_k) * 0.15
            left[k_idx:k_idx + k_len] += kwave
            right[k_idx:k_idx + k_len] += kwave

        # Soft wooden rimshot on beat 1.0 and 3.0
        for s_beat in [1.0, 3.0]:
            st = bar_start + s_beat * beat_dur
            s_idx = int(st * sr)
            s_dur = 0.12
            s_len = int(s_dur * sr)
            t_s = np.linspace(0, s_dur, s_len, False)
            tone = np.sin(2 * np.pi * 480.0 * t_s) * np.exp(-32.0 * t_s) * 0.09
            noise = np.random.uniform(-1.0, 1.0, s_len).astype(np.float32)
            noise_env = np.exp(-28.0 * t_s) * 0.05
            swave = tone + noise * noise_env
            left[s_idx:s_idx + s_len] += swave
            right[s_idx:s_idx + s_len] += swave

        # Brushed swung hi-hat
        for h_step in range(8):
            swing = 0.025 if (h_step % 2 == 1) else 0.0
            ht = bar_start + (h_step * 0.5 + swing) * beat_dur
            h_idx = int(ht * sr)
            h_dur = 0.04
            h_len = int(h_dur * sr)
            t_h = np.linspace(0, h_dur, h_len, False)
            h_noise = np.random.uniform(-1.0, 1.0, h_len).astype(np.float32)
            vol = 0.035 if (h_step % 2 == 0) else 0.018
            hwave = h_noise * np.exp(-55.0 * t_h) * vol
            left[h_idx:h_idx + h_len] += hwave * 0.4
            right[h_idx:h_idx + h_len] += hwave * 0.6

    # Sparse, beautiful melodic motifs (Celesta / Bell tone)
    melody_notes = [
        (8, 1.0, 1.5, 72), (8, 3.0, 1.0, 71),
        (9, 0.5, 2.0, 67),
        (10, 1.0, 1.5, 69), (10, 3.0, 1.0, 72),
        (11, 0.0, 3.0, 71),
        (16, 1.0, 1.5, 76), (16, 3.0, 1.0, 74),
        (17, 0.5, 2.0, 72),
        (18, 1.0, 1.5, 69), (18, 3.0, 1.0, 67),
        (19, 0.0, 3.0, 64),
    ]
    for bar_num, beat_num, dur_beats, midi_note in melody_notes:
        n_t = (bar_num * 4.0 + beat_num) * beat_dur
        n_idx = int(n_t * sr)
        n_dur = dur_beats * beat_dur
        n_len = int(n_dur * sr)
        t_n = np.linspace(0, n_dur, n_len, False)
        freq = midi_to_freq(midi_note)
        env_n = np.exp(-t_n / 1.2) * np.minimum(1.0, t_n / 0.04)
        mwave = (np.sin(2 * np.pi * freq * t_n) + 0.2 * np.sin(2 * np.pi * 2 * freq * t_n)) * env_n * 0.045
        pan = 0.6
        left[n_idx:n_idx + n_len] += mwave * (1.0 - pan)
        right[n_idx:n_idx + n_len] += mwave * pan

    # Ambient tape warmth
    warmth = np.random.uniform(-0.003, 0.003, total_samples).astype(np.float32)
    left += warmth
    right += warmth

    # Fast Stereo Reverb & Loop wrap
    rev_l, rev_r = apply_fast_stereo_reverb(left, right, sr=sr)
    stereo = np.vstack([rev_l, rev_r])
    looped = make_seamless_loop(stereo, loop_samples, tail_samples)

    peak = np.max(np.abs(looped))
    if peak > 0:
        looped = (looped / peak) * 0.75

    return looped, sr


# ==============================================================================
# TRACK 2: "Industrial Pulse" (Ambient Warehouse Soundscape - 32 Bars @ 80 BPM)
# ==============================================================================

def generate_industrial_track():
    bpm = 80.0
    sr = SAMPLE_RATE
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0
    total_bars = 32
    loop_samples = int(total_bars * bar_dur * sr)
    tail_samples = int(4.0 * sr)
    total_samples = loop_samples + tail_samples

    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    # Ambient Chords (each chord spans 2 bars = 8 beats)
    ambient_chords = [
        [40, 52, 55, 59, 62, 66],  # Em9
        [36, 48, 55, 59, 62, 67],  # Cmaj9
        [43, 50, 55, 59, 62, 66],  # Gmaj7
        [47, 50, 54, 57, 62, 66],  # Bm7
        [45, 52, 55, 60, 64, 67],  # Am9
        [38, 50, 54, 57, 62, 64],  # D9
        [43, 50, 55, 59, 62, 66],  # Gmaj7
        [47, 51, 54, 57, 62, 65],  # B7(b13)
        # Part 2
        [36, 48, 55, 59, 62, 67],  # Cmaj9
        [38, 50, 54, 57, 62, 66],  # D6/9
        [40, 52, 55, 59, 62, 66],  # Em9
        [47, 50, 54, 57, 62, 66],  # Bm7
        [36, 48, 55, 59, 62, 67],  # Cmaj9
        [45, 52, 55, 60, 64, 67],  # Am9
        [47, 50, 54, 57, 62, 66],  # Bm7
        [40, 52, 55, 59, 62, 66],  # Em9
    ]

    for chord_idx, chord_midi in enumerate(ambient_chords):
        t_start = (chord_idx * 2) * bar_dur
        start_idx = int(t_start * sr)
        dur = bar_dur * 2.1
        c_len = int(dur * sr)
        t = np.linspace(0, dur, c_len, False)

        attack = np.minimum(1.0, t / 1.5)
        release = np.minimum(1.0, (dur - t) / 1.5)
        env = attack * release

        p_wave_l = np.zeros(c_len, dtype=np.float32)
        p_wave_r = np.zeros(c_len, dtype=np.float32)

        for i, midi_val in enumerate(chord_midi):
            freq = midi_to_freq(midi_val)
            detune = 1.0 + 0.0018 * math.sin(i * 1.3)
            filter_lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t + i * 0.4)
            w1 = np.sin(2 * np.pi * freq * t)
            w2 = 0.35 * np.sin(2 * np.pi * (freq * detune) * 2 * t) * filter_lfo
            w3 = 0.15 * np.sin(2 * np.pi * (freq * 0.5) * t)
            note = (w1 + w2 + w3)

            pan = 0.5 + 0.3 * math.sin(i * 2.1)
            p_wave_l += note * (1.0 - pan)
            p_wave_r += note * pan

        p_wave_l = p_wave_l * env * 0.04
        p_wave_r = p_wave_r * env * 0.04
        end_idx = min(start_idx + c_len, total_samples)
        left[start_idx:end_idx] += p_wave_l[:end_idx - start_idx]
        right[start_idx:end_idx] += p_wave_r[:end_idx - start_idx]

    # Delicate Kalimba / Drop Arpeggio (Atmospheric, sparse)
    kalimba_notes = [64, 67, 71, 74, 76, 79, 83]
    for bar in range(total_bars):
        if bar % 2 == 1:
            for note_beat in [1.5, 3.25]:
                k_t = (bar * bar_dur) + (note_beat * beat_dur)
                k_idx = int(k_t * sr)
                k_dur = 1.8
                k_len = int(k_dur * sr)
                t_k = np.linspace(0, k_dur, k_len, False)
                midi_val = kalimba_notes[(bar * 3 + int(note_beat * 2)) % len(kalimba_notes)]
                freq = midi_to_freq(midi_val)
                k_env = np.exp(-t_k / 0.6) * np.minimum(1.0, t_k / 0.01)
                kwave = (np.sin(2 * np.pi * freq * t_k) + 0.25 * np.sin(2 * np.pi * 3.0 * freq * t_k) * np.exp(-t_k / 0.15)) * k_env * 0.04
                pan = 0.5 + 0.35 * math.sin(bar * 1.9)
                left[k_idx:k_idx + k_len] += kwave * (1.0 - pan)
                right[k_idx:k_idx + k_len] += kwave * pan

    # Sub-bass warmth
    for chord_idx, chord_midi in enumerate(ambient_chords):
        t_start = (chord_idx * 2) * bar_dur
        start_idx = int(t_start * sr)
        dur = bar_dur * 2.0
        b_len = int(dur * sr)
        t = np.linspace(0, dur, b_len, False)
        root_midi = chord_midi[0]
        freq = midi_to_freq(root_midi)
        attack = np.minimum(1.0, t / 0.6)
        release = np.minimum(1.0, (dur - t) / 0.6)
        sub = np.sin(2 * np.pi * freq * t) * attack * release * 0.14
        end_idx = min(start_idx + b_len, total_samples)
        left[start_idx:end_idx] += sub[:end_idx - start_idx] * 0.5
        right[start_idx:end_idx] += sub[:end_idx - start_idx] * 0.5

    # Gentle clockwork acoustic tick every 2 beats
    for bar in range(total_bars):
        for tick_beat in [0.0, 2.0]:
            t_t = (bar * bar_dur) + (tick_beat * beat_dur)
            t_idx = int(t_t * sr)
            t_dur = 0.03
            t_len = int(t_dur * sr)
            tt = np.linspace(0, t_dur, t_len, False)
            tick = np.sin(2 * np.pi * 1200.0 * tt) * np.exp(-85.0 * tt) * 0.015
            left[t_idx:t_idx + t_len] += tick * 0.5
            right[t_idx:t_idx + t_len] += tick * 0.5

    rev_l, rev_r = apply_fast_stereo_reverb(left, right, sr=sr)
    stereo = np.vstack([rev_l, rev_r])
    looped = make_seamless_loop(stereo, loop_samples, tail_samples)

    peak = np.max(np.abs(looped))
    if peak > 0:
        looped = (looped / peak) * 0.72

    return looped, sr


def export_audio_to_ogg(stereo_data, sr, base_filename, lpf_cutoff=4200):
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

    # Studio-grade mastering chain via FFmpeg
    af_chain = (
        f"lowpass=f={lpf_cutoff},"
        "highpass=f=28,"
        "stereowiden=70,"
        "acompressor=threshold=-18dB:ratio=2.5:attack=10:release=120"
    )

    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-af", af_chain,
        "-c:a", "libvorbis", "-q:a", "4",
        ogg_path
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(wav_path):
        os.remove(wav_path)
    sz = os.path.getsize(ogg_path)
    print(f"Generated {ogg_path} ({sz / 1024:.1f} KB)")


if __name__ == "__main__":
    print("Generating Studio-Grade 'Warehouse Chill' (Lo-Fi Study / Puzzle Beats)...")
    lofi_audio, sr = generate_lofi_track()
    export_audio_to_ogg(lofi_audio, sr, "bgm_lofi_shift", lpf_cutoff=4200)

    print("Generating Studio-Grade 'Industrial Pulse' (Ambient Warehouse Soundscape)...")
    ind_audio, sr = generate_industrial_track()
    export_audio_to_ogg(ind_audio, sr, "bgm_industrial_pulse", lpf_cutoff=4600)
    print("All BGM tracks rendered successfully!")
