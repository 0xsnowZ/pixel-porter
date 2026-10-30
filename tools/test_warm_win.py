import math

MIX_RATE = 22050

def generate_warm_bell_win():
    # 0.52s total duration: clean, cheerful, sweet, non-fatiguing
    duration = 0.52
    total_samples = int(duration * MIX_RATE)
    
    # 4-note sweet marimba / bell arpeggio: C5 -> E5 -> G5 -> C6
    notes = [
        {"start": 0.00, "end": 0.11, "freq": 523.25}, # C5
        {"start": 0.10, "end": 0.22, "freq": 659.25}, # E5
        {"start": 0.21, "end": 0.34, "freq": 783.99}, # G5
        {"start": 0.32, "end": 0.52, "freq": 1046.50}, # C6 (held with warm bell ring)
    ]
    
    samples = []
    max_val = 0.0
    
    # Precompute note phases
    for i in range(total_samples):
        t = i / MIX_RATE
        val = 0.0
        
        for n in notes:
            if t >= n["start"] and t < n["end"]:
                dt = t - n["start"]
                note_len = n["end"] - n["start"]
                # Soft percussion attack (4ms) to eliminate clicks
                att = min(1.0, dt / 0.005)
                # Warm bell decay
                rel_t = dt / note_len
                # Final note has longer ring
                decay_exp = 1.6 if n["freq"] == 1046.50 else 2.2
                env = att * math.pow(max(0.0, 1.0 - rel_t), decay_exp)
                
                # Pure warm bell synthesis:
                # Fundamental + gentle 2nd harmonic (octave) + subtle 3rd harmonic
                p1 = 2.0 * math.pi * n["freq"] * dt
                p2 = 2.0 * math.pi * (n["freq"] * 2.0) * dt
                p3 = 2.0 * math.pi * (n["freq"] * 3.0) * dt
                
                bell_wave = 0.70 * math.sin(p1) + 0.22 * math.sin(p2) + 0.08 * math.sin(p3)
                val += bell_wave * env * 0.85
                
        max_val = max(max_val, abs(val))
        samples.append(val)
        
    print(f'Max amplitude: {max_val:.2f}, total samples: {len(samples)}')
    return samples

generate_warm_bell_win()

