# How To: Encode Symmetry

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Positive and negative values should encode symmetrically.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `vision_agents.plugins.twilio.audio`


## Step-by-Step Guide

### Step 1: 'Positive and negative values should encode symmetrically.'

```python
'Positive and negative values should encode symmetrically.'
```

**Verification:**
```python
assert pos_mulaw & 127 == neg_mulaw & 127, f'Asymmetric encoding for ±{val}: pos={pos_mulaw:#04x}, neg={neg_mulaw:#04x}'
```

### Step 2: Assign test_values = value

```python
test_values = [100, 1000, 8000, 16000, 32000]
```

### Step 3: Assign pos_pcm = PcmData(...)

```python
pos_pcm = PcmData(samples=np.array([val], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

### Step 4: Assign neg_pcm = PcmData(...)

```python
neg_pcm = PcmData(samples=np.array([-val], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

### Step 5: Assign pos_mulaw = value

```python
pos_mulaw = pcm_to_mulaw(pos_pcm)[0]
```

### Step 6: Assign neg_mulaw = value

```python
neg_mulaw = pcm_to_mulaw(neg_pcm)[0]
```

**Verification:**
```python
assert pos_mulaw & 127 == neg_mulaw & 127, f'Asymmetric encoding for ±{val}: pos={pos_mulaw:#04x}, neg={neg_mulaw:#04x}'
```


## Complete Example

```python
# Workflow
'Positive and negative values should encode symmetrically.'
test_values = [100, 1000, 8000, 16000, 32000]
for val in test_values:
    pos_pcm = PcmData(samples=np.array([val], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
    neg_pcm = PcmData(samples=np.array([-val], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
    pos_mulaw = pcm_to_mulaw(pos_pcm)[0]
    neg_mulaw = pcm_to_mulaw(neg_pcm)[0]
    assert pos_mulaw & 127 == neg_mulaw & 127, f'Asymmetric encoding for ±{val}: pos={pos_mulaw:#04x}, neg={neg_mulaw:#04x}'
```

## Next Steps


---

*Source: test_audio.py:359 | Complexity: Intermediate | Last updated: 2026-04-12*