# How To: No Clipping Distortion

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Ensure we don't introduce clipping at signal boundaries.

## Prerequisites

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `vision_agents.plugins.twilio.audio`


## Step-by-Step Guide

### Step 1: "Ensure we don't introduce clipping at signal boundaries."

```python
"Ensure we don't introduce clipping at signal boundaries."
```

**Verification:**
```python
assert np.all(recovered.samples >= -32768)
```

### Step 2: Assign edge_values = np.array(...)

```python
edge_values = np.array([-32768, -32767, 32766, 32767], dtype=np.int16)
```

**Verification:**
```python
assert np.all(recovered.samples <= 32767)
```

### Step 3: Assign pcm = PcmData(...)

```python
pcm = PcmData(samples=edge_values, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

**Verification:**
```python
assert recovered.samples[0] < 0
```

### Step 4: Assign mulaw = pcm_to_mulaw(...)

```python
mulaw = pcm_to_mulaw(pcm)
```

**Verification:**
```python
assert recovered.samples[1] < 0
```

### Step 5: Assign recovered = mulaw_to_pcm(...)

```python
recovered = mulaw_to_pcm(mulaw)
```

**Verification:**
```python
assert recovered.samples[2] > 0
```


## Complete Example

```python
# Workflow
"Ensure we don't introduce clipping at signal boundaries."
edge_values = np.array([-32768, -32767, 32766, 32767], dtype=np.int16)
pcm = PcmData(samples=edge_values, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
mulaw = pcm_to_mulaw(pcm)
recovered = mulaw_to_pcm(mulaw)
assert np.all(recovered.samples >= -32768)
assert np.all(recovered.samples <= 32767)
assert recovered.samples[0] < 0
assert recovered.samples[1] < 0
assert recovered.samples[2] > 0
assert recovered.samples[3] > 0
```

## Next Steps


---

*Source: test_audio.py:498 | Complexity: Intermediate | Last updated: 2026-04-12*