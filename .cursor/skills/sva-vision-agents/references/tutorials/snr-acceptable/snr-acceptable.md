# How To: Snr Acceptable

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Verify Signal-to-Noise Ratio is acceptable for voice.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `vision_agents.plugins.twilio.audio`


## Step-by-Step Guide

### Step 1: 'Verify Signal-to-Noise Ratio is acceptable for voice.'

```python
'Verify Signal-to-Noise Ratio is acceptable for voice.'
```

**Verification:**
```python
assert snr_db > 35, f'SNR too low: {snr_db:.1f} dB'
```

### Step 2: Assign duration = 0.5

```python
duration = 0.5
```

### Step 3: Assign samples_count = int(...)

```python
samples_count = int(TWILIO_SAMPLE_RATE * duration)
```

### Step 4: Assign t = np.linspace(...)

```python
t = np.linspace(0, duration, samples_count, dtype=np.float32)
```

### Step 5: Assign signal = unknown.astype(...)

```python
signal = (np.sin(2 * np.pi * 200 * t) * 8000 + np.sin(2 * np.pi * 400 * t) * 6000 + np.sin(2 * np.pi * 800 * t) * 4000).astype(np.int16)
```

### Step 6: Assign original = PcmData(...)

```python
original = PcmData(samples=signal, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

### Step 7: Assign mulaw = pcm_to_mulaw(...)

```python
mulaw = pcm_to_mulaw(original)
```

### Step 8: Assign recovered = mulaw_to_pcm(...)

```python
recovered = mulaw_to_pcm(mulaw)
```

### Step 9: Assign signal_power = np.mean(...)

```python
signal_power = np.mean(original.samples.astype(np.float64) ** 2)
```

### Step 10: Assign noise = value

```python
noise = original.samples.astype(np.float64) - recovered.samples.astype(np.float64)
```

### Step 11: Assign noise_power = np.mean(...)

```python
noise_power = np.mean(noise ** 2)
```

### Step 12: Assign snr_db = value

```python
snr_db = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
```

**Verification:**
```python
assert snr_db > 35, f'SNR too low: {snr_db:.1f} dB'
```


## Complete Example

```python
# Workflow
'Verify Signal-to-Noise Ratio is acceptable for voice.'
duration = 0.5
samples_count = int(TWILIO_SAMPLE_RATE * duration)
t = np.linspace(0, duration, samples_count, dtype=np.float32)
signal = (np.sin(2 * np.pi * 200 * t) * 8000 + np.sin(2 * np.pi * 400 * t) * 6000 + np.sin(2 * np.pi * 800 * t) * 4000).astype(np.int16)
original = PcmData(samples=signal, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
mulaw = pcm_to_mulaw(original)
recovered = mulaw_to_pcm(mulaw)
signal_power = np.mean(original.samples.astype(np.float64) ** 2)
noise = original.samples.astype(np.float64) - recovered.samples.astype(np.float64)
noise_power = np.mean(noise ** 2)
snr_db = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
assert snr_db > 35, f'SNR too low: {snr_db:.1f} dB'
```

## Next Steps


---

*Source: test_audio.py:457 | Complexity: Advanced | Last updated: 2026-04-12*