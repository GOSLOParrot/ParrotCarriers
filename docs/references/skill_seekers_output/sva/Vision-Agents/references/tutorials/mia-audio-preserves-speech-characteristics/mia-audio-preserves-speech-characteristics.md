# How To: Mia Audio Preserves Speech Characteristics

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that mulaw conversion preserves speech-like characteristics.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `numpy`
- `getstream.video.rtc.track_util`
- `importlib.util`
- `os`

**Setup Required:**
```python
# Fixtures: mia_audio_16khz
```

## Step-by-Step Guide

### Step 1: 'Test that mulaw conversion preserves speech-like characteristics.'

```python
'Test that mulaw conversion preserves speech-like characteristics.'
```

**Verification:**
```python
assert samples.max() > 1000, 'Audio should have positive peaks'
```

### Step 2: Assign mulaw_bytes = pcm_to_mulaw(...)

```python
mulaw_bytes = pcm_to_mulaw(mia_audio_16khz)
```

**Verification:**
```python
assert samples.min() < -1000, 'Audio should have negative peaks'
```

### Step 3: Assign recovered = mulaw_to_pcm(...)

```python
recovered = mulaw_to_pcm(mulaw_bytes)
```

**Verification:**
```python
assert unique_values > 50, 'Audio should have variation'
```

### Step 4: Assign samples = value

```python
samples = recovered.samples
```

**Verification:**
```python
assert samples.max() > 1000, 'Audio should have positive peaks'
```

### Step 5: Assign unique_values = len(...)

```python
unique_values = len(np.unique(samples))
```

**Verification:**
```python
assert unique_values > 50, 'Audio should have variation'
```


## Complete Example

```python
# Setup
# Fixtures: mia_audio_16khz

# Workflow
'Test that mulaw conversion preserves speech-like characteristics.'
mulaw_bytes = pcm_to_mulaw(mia_audio_16khz)
recovered = mulaw_to_pcm(mulaw_bytes)
samples = recovered.samples
assert samples.max() > 1000, 'Audio should have positive peaks'
assert samples.min() < -1000, 'Audio should have negative peaks'
unique_values = len(np.unique(samples))
assert unique_values > 50, 'Audio should have variation'
```

## Next Steps


---

*Source: test_mulaw_conversion.py:89 | Complexity: Intermediate | Last updated: 2026-04-12*