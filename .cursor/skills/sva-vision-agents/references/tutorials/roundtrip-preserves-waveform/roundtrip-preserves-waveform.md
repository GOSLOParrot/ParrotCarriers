# How To: Roundtrip Preserves Waveform

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Verify PCM -> mulaw -> PCM round-trip maintains signal quality.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `vision_agents.plugins.twilio.audio`


## Step-by-Step Guide

### Step 1: 'Verify PCM -> mulaw -> PCM round-trip maintains signal quality.'

```python
'Verify PCM -> mulaw -> PCM round-trip maintains signal quality.'
```

**Verification:**
```python
assert max_error < 2000, f'Max error too high: {max_error}'
```

### Step 2: Assign duration = 0.1

```python
duration = 0.1
```

**Verification:**
```python
assert mean_error < 500, f'Mean error too high: {mean_error}'
```

### Step 3: Assign t = np.linspace(...)

```python
t = np.linspace(0, duration, int(TWILIO_SAMPLE_RATE * duration), dtype=np.float32)
```

### Step 4: Assign sine_wave = unknown.astype(...)

```python
sine_wave = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)
```

### Step 5: Assign original_pcm = PcmData(...)

```python
original_pcm = PcmData(samples=sine_wave, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

### Step 6: Assign mulaw = pcm_to_mulaw(...)

```python
mulaw = pcm_to_mulaw(original_pcm)
```

### Step 7: Assign recovered_pcm = mulaw_to_pcm(...)

```python
recovered_pcm = mulaw_to_pcm(mulaw)
```

### Step 8: Assign error = np.abs(...)

```python
error = np.abs(original_pcm.samples.astype(np.int32) - recovered_pcm.samples.astype(np.int32))
```

### Step 9: Assign max_error = np.max(...)

```python
max_error = np.max(error)
```

### Step 10: Assign mean_error = np.mean(...)

```python
mean_error = np.mean(error)
```

**Verification:**
```python
assert max_error < 2000, f'Max error too high: {max_error}'
```


## Complete Example

```python
# Workflow
'Verify PCM -> mulaw -> PCM round-trip maintains signal quality.'
duration = 0.1
t = np.linspace(0, duration, int(TWILIO_SAMPLE_RATE * duration), dtype=np.float32)
sine_wave = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)
original_pcm = PcmData(samples=sine_wave, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
mulaw = pcm_to_mulaw(original_pcm)
recovered_pcm = mulaw_to_pcm(mulaw)
error = np.abs(original_pcm.samples.astype(np.int32) - recovered_pcm.samples.astype(np.int32))
max_error = np.max(error)
mean_error = np.mean(error)
assert max_error < 2000, f'Max error too high: {max_error}'
assert mean_error < 500, f'Mean error too high: {mean_error}'
```

## Next Steps


---

*Source: test_audio.py:391 | Complexity: Advanced | Last updated: 2026-04-12*