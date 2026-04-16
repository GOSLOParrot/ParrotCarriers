# How To: Mia Audio 16Khz

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: mia audio 16khz

## Prerequisites

**Required Modules:**
- `asyncio`
- `os`
- `numpy`
- `pytest`
- `torchvision.io.video`
- `getstream.video.rtc.track_util`
- `aiortc`


## Step-by-Step Guide

### Step 1: Assign audio_file_path = os.path.join(...)

```python
audio_file_path = os.path.join(os.path.dirname(__file__), 'test_assets/mia.mp3')
```

### Step 2: 'Load mia.mp3 and convert to 16kHz PCM data'

```python
'Load mia.mp3 and convert to 16kHz PCM data'
```

### Step 3: Assign container = av.open(...)

```python
container = av.open(audio_file_path)
```

### Step 4: Assign audio_stream = value

```python
audio_stream = container.streams.audio[0]
```

### Step 5: Assign original_sample_rate = value

```python
original_sample_rate = audio_stream.sample_rate
```

### Step 6: Assign target_rate = 16000

```python
target_rate = 16000
```

### Step 7: Assign resampler = None

```python
resampler = None
```

### Step 8: Assign samples = value

```python
samples = []
```

### Step 9: Assign samples = np.concatenate(...)

```python
samples = np.concatenate(samples)
```

### Step 10: Assign samples = samples.astype(...)

```python
samples = samples.astype(np.int16)
```

### Step 11: Call container.close()

```python
container.close()
```

### Step 12: Assign pcm = PcmData(...)

```python
pcm = PcmData(samples=samples, sample_rate=target_rate, format=AudioFormat.S16)
```

### Step 13: Assign resampler = av.AudioResampler(...)

```python
resampler = av.AudioResampler(format=AudioFormat.S16, layout='mono', rate=target_rate)
```

### Step 14: Assign frame_array = frame.to_ndarray(...)

```python
frame_array = frame.to_ndarray()
```

### Step 15: Call samples.append()

```python
samples.append(frame_array)
```

### Step 16: Assign frame = value

```python
frame = resampler.resample(frame)[0]
```

### Step 17: Assign frame_array = np.mean(...)

```python
frame_array = np.mean(frame_array, axis=0)
```


## Complete Example

```python
# Workflow
audio_file_path = os.path.join(os.path.dirname(__file__), 'test_assets/mia.mp3')
'Load mia.mp3 and convert to 16kHz PCM data'
container = av.open(audio_file_path)
audio_stream = container.streams.audio[0]
original_sample_rate = audio_stream.sample_rate
target_rate = 16000
resampler = None
if original_sample_rate != target_rate:
    resampler = av.AudioResampler(format=AudioFormat.S16, layout='mono', rate=target_rate)
samples = []
for frame in container.decode(audio_stream):
    if resampler:
        frame = resampler.resample(frame)[0]
    frame_array = frame.to_ndarray()
    if len(frame_array.shape) > 1:
        frame_array = np.mean(frame_array, axis=0)
    samples.append(frame_array)
samples = np.concatenate(samples)
samples = samples.astype(np.int16)
container.close()
pcm = PcmData(samples=samples, sample_rate=target_rate, format=AudioFormat.S16)
return pcm
```

## Next Steps


---

*Source: base_test.py:18 | Complexity: Advanced | Last updated: 2026-04-12*