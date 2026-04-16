# How To: Roundtrip Known Values

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Verify round-trip produces expected decoded values.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `vision_agents.plugins.twilio.audio`


## Step-by-Step Guide

### Step 1: 'Verify round-trip produces expected decoded values.'

```python
'Verify round-trip produces expected decoded values.'
```

**Verification:**
```python
assert recovered == expected_recovered, f'Round-trip mismatch for PCM {original}: got {recovered}, expected {expected_recovered}'
```

### Step 2: Assign test_cases = value

```python
test_cases = [(0, 0), (32767, 32124), (-32768, -32124), (16000, 15996), (-16000, -15996), (1000, 988), (-1000, -988)]
```

### Step 3: Assign pcm = PcmData(...)

```python
pcm = PcmData(samples=np.array([original], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

### Step 4: Assign mulaw = pcm_to_mulaw(...)

```python
mulaw = pcm_to_mulaw(pcm)
```

### Step 5: Assign recovered = value

```python
recovered = mulaw_to_pcm(mulaw).samples[0]
```

**Verification:**
```python
assert recovered == expected_recovered, f'Round-trip mismatch for PCM {original}: got {recovered}, expected {expected_recovered}'
```


## Complete Example

```python
# Workflow
'Verify round-trip produces expected decoded values.'
test_cases = [(0, 0), (32767, 32124), (-32768, -32124), (16000, 15996), (-16000, -15996), (1000, 988), (-1000, -988)]
for original, expected_recovered in test_cases:
    pcm = PcmData(samples=np.array([original], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
    mulaw = pcm_to_mulaw(pcm)
    recovered = mulaw_to_pcm(mulaw).samples[0]
    assert recovered == expected_recovered, f'Round-trip mismatch for PCM {original}: got {recovered}, expected {expected_recovered}'
```

## Next Steps


---

*Source: test_audio.py:424 | Complexity: Intermediate | Last updated: 2026-04-12*