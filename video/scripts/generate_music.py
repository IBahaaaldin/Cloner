import wave, math, struct, random, subprocess, os

SAMPLE_RATE = 44100
OUT_DIR = "/Users/bahaam/Desktop/Cloner/video/public/audio"
os.makedirs(OUT_DIR, exist_ok=True)

def create_whoosh():
    duration = 0.45
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        noise = random.uniform(-1, 1)
        if t < 0.28:
            env = (t / 0.28) ** 2
            freq = 180 + 1400 * (t / 0.28)
        else:
            decay_t = (t - 0.28) / 0.17
            env = max(0.0, (1.0 - decay_t) ** 2)
            freq = 1580 - 1100 * decay_t
        tone = math.sin(2 * math.pi * freq * t)
        val = (noise * 0.45 + tone * 0.55) * env * 0.75
        val = max(-1.0, min(1.0, val))
        samples.append(int(val * 32767))
    
    wav_path = "/tmp/whoosh.wav"
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in samples:
            wf.writeframes(struct.pack("<h", s))
    
    mp3_path = os.path.join(OUT_DIR, "whoosh.mp3")
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, mp3_path], stderr=subprocess.DEVNULL)

def create_bgm():
    duration = 22.0
    bpm = 124.0
    beat_dur = 60.0 / bpm
    num_samples = int(duration * SAMPLE_RATE)
    samples = [0.0] * num_samples

    # Kick drum on every beat
    for beat in range(int(duration / beat_dur)):
        start_idx = int(beat * beat_dur * SAMPLE_RATE)
        kick_samples = int(0.18 * SAMPLE_RATE)
        for i in range(kick_samples):
            if start_idx + i >= num_samples: break
            t = i / SAMPLE_RATE
            freq = 140 * math.exp(-t * 28) + 45
            env = math.exp(-t * 18)
            samples[start_idx + i] += math.sin(2 * math.pi * freq * t) * env * 0.65

    # Hi-hat on off-beats (8th notes)
    for hat in range(int(duration / (beat_dur / 2))):
        if hat % 2 == 1:
            start_idx = int(hat * (beat_dur / 2) * SAMPLE_RATE)
            hat_samples = int(0.05 * SAMPLE_RATE)
            for i in range(hat_samples):
                if start_idx + i >= num_samples: break
                t = i / SAMPLE_RATE
                env = math.exp(-t * 80)
                noise = random.uniform(-1, 1)
                samples[start_idx + i] += noise * env * 0.18

    # Bassline notes (F - Ab - Bb - Eb progression)
    notes = [43.65, 51.91, 58.27, 38.89]
    bar_dur = beat_dur * 4
    for bar in range(int(duration / bar_dur) + 1):
        note = notes[bar % len(notes)]
        for sub in range(4):
            start_idx = int((bar * bar_dur + sub * beat_dur) * SAMPLE_RATE)
            dur = int(beat_dur * 0.7 * SAMPLE_RATE)
            for i in range(dur):
                if start_idx + i >= num_samples: break
                t = i / SAMPLE_RATE
                env = math.exp(-t * 4.5)
                mod = math.sin(2 * math.pi * (note * 2) * t) * 1.5
                carrier = math.sin(2 * math.pi * note * t + mod)
                samples[start_idx + i] += carrier * env * 0.35

    # Arpeggio synth chords
    arp_scale = [261.63, 311.13, 349.23, 392.00, 466.16, 523.25]
    step_dur = beat_dur / 4
    num_steps = int(duration / step_dur)
    for step in range(num_steps):
        note = arp_scale[step % len(arp_scale)]
        start_idx = int(step * step_dur * SAMPLE_RATE)
        dur = int(step_dur * 0.8 * SAMPLE_RATE)
        for i in range(dur):
            if start_idx + i >= num_samples: break
            t = i / SAMPLE_RATE
            env = math.exp(-t * 15)
            tone = math.sin(2 * math.pi * note * t) + 0.3 * math.sin(2 * math.pi * note * 2 * t)
            samples[start_idx + i] += tone * env * 0.12

    max_val = max(abs(s) for s in samples) or 1.0
    int_samples = []
    for s in samples:
        norm = s / max_val
        saturated = math.tanh(norm * 1.2) * 0.85
        int_samples.append(int(saturated * 32767))

    wav_path = "/tmp/bgm.wav"
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in int_samples:
            wf.writeframes(struct.pack("<h", s))

    mp3_path = os.path.join(OUT_DIR, "bgm.mp3")
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, mp3_path], stderr=subprocess.DEVNULL)
    print("Generated all audio files successfully.")

if __name__ == "__main__":
    create_whoosh()
    create_bgm()
