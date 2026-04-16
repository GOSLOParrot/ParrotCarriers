# How To: Pcm To Mulaw And Back

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test roundtrip conversion preserves audio structure.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `importlib.util`
- `os`


## Step-by-Step Guide

### Step 1: 'Test roundtrip conversion preserves audio structure.'

```python
'Test roundtrip conversion preserves audio structure.'
```

**Verification:**
```python
assert recovered.sample_rate == TWILIO_SAMPLE_RATE
```

### Step 2: Assign samples = np.array(...)

```python
samples = np.array([100, 1000, -1000, 16000, -16000, 32000, -32000], dtype=np.int16)
```

**Verification:**
```python
assert recovered.channels == 1
```

### Step 3: Assign pcm = PcmData(...)

```python
pcm = PcmData(samples=samples, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

**Verification:**
```python
assert len(recovered.samples) == len(samples)
```

### Step 4: Assign mulaw_bytes = pcm_to_mulaw(...)

```python
mulaw_bytes = pcm_to_mulaw(pcm)
```

### Step 5: Assign recovered = mulaw_to_pcm(...)

```python
recovered = mulaw_to_pcm(mulaw_bytes)
```

**Verification:**
```python
assert recovered.sample_rate == TWILIO_SAMPLE_RATE
```

### Step 6: Assign original_signs = np.sign(...)

```python
original_signs = np.sign(samples)
```

### Step 7: Assign recovered_signs = np.sign(...)

```python
recovered_signs = np.sign(recovered.samples)
```

### Step 8: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal(original_signs, recovered_signs)
```


## Complete Example

```python
# Workflow
'Test roundtrip conversion preserves audio structure.'
samples = np.array([100, 1000, -1000, 16000, -16000, 32000, -32000], dtype=np.int16)
pcm = PcmData(samples=samples, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
mulaw_bytes = pcm_to_mulaw(pcm)
recovered = mulaw_to_pcm(mulaw_bytes)
assert recovered.sample_rate == TWILIO_SAMPLE_RATE
assert recovered.channels == 1
assert len(recovered.samples) == len(samples)
original_signs = np.sign(samples)
recovered_signs = np.sign(recovered.samples)
np.testing.assert_array_equal(original_signs, recovered_signs)
```

## Next Steps


---

*Source: test_mulaw_conversion.py:25 | Complexity: Advanced | Last updated: 2026-04-12*