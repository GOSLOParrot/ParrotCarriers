# How To: Pcm To Mulaw Resamples

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that pcm_to_mulaw resamples non-8kHz audio.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `importlib.util`
- `os`


## Step-by-Step Guide

### Step 1: 'Test that pcm_to_mulaw resamples non-8kHz audio.'

```python
'Test that pcm_to_mulaw resamples non-8kHz audio.'
```

**Verification:**
```python
assert len(mulaw_bytes) == len(samples) // 2
```

### Step 2: Assign samples = value

```python
samples = np.sin(np.linspace(0, 2 * np.pi, 160)) * 10000
```

### Step 3: Assign samples = samples.astype(...)

```python
samples = samples.astype(np.int16)
```

### Step 4: Assign pcm = PcmData(...)

```python
pcm = PcmData(samples=samples, sample_rate=16000, channels=1, format=AudioFormat.S16)
```

### Step 5: Assign mulaw_bytes = pcm_to_mulaw(...)

```python
mulaw_bytes = pcm_to_mulaw(pcm)
```

**Verification:**
```python
assert len(mulaw_bytes) == len(samples) // 2
```


## Complete Example

```python
# Workflow
'Test that pcm_to_mulaw resamples non-8kHz audio.'
samples = np.sin(np.linspace(0, 2 * np.pi, 160)) * 10000
samples = samples.astype(np.int16)
pcm = PcmData(samples=samples, sample_rate=16000, channels=1, format=AudioFormat.S16)
mulaw_bytes = pcm_to_mulaw(pcm)
assert len(mulaw_bytes) == len(samples) // 2
```

## Next Steps


---

*Source: test_mulaw_conversion.py:61 | Complexity: Intermediate | Last updated: 2026-04-12*