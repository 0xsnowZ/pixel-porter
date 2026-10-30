import math
import struct

MIX_RATE = 22050

def generate_win_wav():
    duration = 1.35
    total_samples = int(duration * MIX_RATE)
    
    # 7-note fanfare motif:
    # G4, C5, E5, G5, C6 (accent), B5 (turn), C6 (grand sustained finale)
    notes = [
        (0.00, 0.09, 392.00, 0.65),  # G4
        (0.09, 0.18, 523.25, 0.75),  # C5
        (0.18, 0.27, 659.25, 0.85),  # E5
        (0.27, 0.36, 783.99, 0.90),  # G5
        (0.36, 0.54, 1046.50, 1.00), # C6 (accent)
        (0.54, 0.63, 987.77, 0.80),  # B5 (grace)
        (0.63, 1.35, 1046.50, 1.00), # C6 (grand sustained finale)
    ]
    
    # Sustained harmonic backing chord during finale (0.63 to 1.35s)
    # C3 (bass), C4, E4, G4, E5, G5
    backing_chords = [
        (0.63, 1.35, 130.81, 0.45), # C3 sub bass
        (0.63, 1.35, 261.63, 0.40), # C4 root
        (0.63, 1.35, 329.63, 0.35), # E4 third
        (0.63, 1.35, 392.00, 0.35), # G4 fifth
        (0.63, 1.35, 659.25, 0.30), # E5
    ]
    
    # Sparkle / chime glitter arpeggio over finale
    sparkles = [
        (0.68, 1.10, 2093.00, 0.20), # C7
        (0.78, 1.15, 2637.02, 0.18), # E7
        (0.88, 1.20, 3135.96, 0.15), # G7
        (0.98, 1.25, 4186.01, 0.12), # C8
    ]
    
    samples = []
    max_val = 0.0
    
    for i in range(total_samples):
        t = i / MIX_RATE
        val = 0.0
        
        # 1. Lead Melody
        for start, end, freq, gain in notes:
            if start <= t < end:
                dt = t - start
                note_len = end - start
                # Envelope: quick attack (8ms), exponential decay
                att = min(1.0, dt / 0.008)
                if end == 1.35: # finale note decays slowly
                    rel_t = (t - start) / (end - start)
                    env = att * (1.0 - rel_t * 0.75) * math.exp(-rel_t * 1.5)
                else:
                    rel_t = dt / note_len
                    env = att * (1.0 - rel_t * 0.35)
                
                # Vibrato on sustained finale
                vib = 0.0
                if t > 0.70:
                    vib = 5.0 * math.sin(2.0 * math.pi * 6.0 * (t - 0.70))
                
                phase = 2.0 * math.pi * (freq + vib) * dt
                # Pulse wave with 30% duty cycle + sine harmonic for fullness
                pulse = 1.0 if (phase % (2.0 * math.pi)) < (2.0 * math.pi * 0.35) else -1.0
                sine = math.sin(phase)
                lead_wave = 0.65 * pulse + 0.35 * sine
                val += lead_wave * env * gain * 0.45
                break
                
        # 2. Harmonic Backing Chord during finale
        for start, end, freq, gain in backing_chords:
            if start <= t < end:
                dt = t - start
                rel_t = dt / (end - start)
                att = min(1.0, dt / 0.02)
                env = att * (1.0 - rel_t * 0.8) * math.exp(-rel_t * 1.8)
                phase = 2.0 * math.pi * freq * dt
                # Warm sawtooth / sine mix
                chord_wave = 0.5 * math.sin(phase) + 0.5 * (1.0 - (phase % (2.0 * math.pi)) / math.pi)
                val += chord_wave * env * gain * 0.35
                
        # 3. Crystalline Sparkles
        for start, end, freq, gain in sparkles:
            if start <= t < end:
                dt = t - start
                att = min(1.0, dt / 0.004)
                rel_t = dt / (end - start)
                env = att * math.exp(-rel_t * 5.0)
                sparkle_wave = math.sin(2.0 * math.pi * freq * dt)
                val += sparkle_wave * env * gain * 0.25
                
        max_val = max(max_val, abs(val))
        samples.append(val)
        
    print(f'Max unnormalized amplitude: {max_val:.2f}')
    # Normalize to 0.88 to ensure zero clipping with maximum dynamic punch
    norm_factor = 0.88 / max(max_val, 0.001)
    int_samples = [int(s * norm_factor * 32767.0) for s in samples]
    print(f'Total samples: {len(int_samples)}, Peak sample: {max(abs(s) for s in int_samples)}')
    return int_samples

generate_win_wav()

