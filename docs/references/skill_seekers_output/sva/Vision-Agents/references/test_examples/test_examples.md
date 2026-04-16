# Test Example Extraction Report

**Total Examples**: 132  
**High Value Examples** (confidence > 0.7): 132  
**Average Complexity**: 0.27  

## Examples by Category

- **instantiation**: 93
- **method_call**: 27
- **workflow**: 12

## Examples by Language

- **Python**: 132

## Extracted Examples

### mia_audio_16khz

**Category**: workflow  
**Description**: Workflow: mia audio 16khz  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:18*

### test_create_and_get

**Category**: workflow  
**Description**: Workflow: Test creating and retrieving calls.  
**Expected**: assert retrieved is call  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test creating and retrieving calls.'
registry = twilio.TwilioCallRegistry()
webhook_data = CallWebhookInput(CallSid='CA123', AccountSid='AC123', CallStatus='ringing', Direction='inbound', From='+123', Caller='+123', To='+456', Called='+456')
call = registry.create('CA123', webhook_data=webhook_data)
assert call.call_sid == 'CA123'
assert call.from_number == '+123'
retrieved = registry.get('CA123')
assert retrieved is call
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:55*

### test_parse_file_outside_base_dir

**Category**: workflow  
**Description**: Workflow: test parse file outside base dir  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

file_path1 = tmp_path / 'file1.md'
base_dir = tmp_path / 'another-dir'
base_dir.mkdir()
file_path2 = base_dir / 'file1.md'
input_text = f'read @{file_path1}'
file_path1.write_text('abcdef', encoding='utf-8')
file_path2.write_text('abcdef', encoding='utf-8')
with pytest.raises(InstructionsReadError, match='reason - path outside the base directory'):
    Instructions(input_text=input_text, base_dir=base_dir)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_instructions.py:55*

### test_encode_symmetry

**Category**: workflow  
**Description**: Workflow: Positive and negative values should encode symmetrically.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Positive and negative values should encode symmetrically.'
test_values = [100, 1000, 8000, 16000, 32000]
for val in test_values:
    pos_pcm = PcmData(samples=np.array([val], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
    neg_pcm = PcmData(samples=np.array([-val], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
    pos_mulaw = pcm_to_mulaw(pos_pcm)[0]
    neg_mulaw = pcm_to_mulaw(neg_pcm)[0]
    assert pos_mulaw & 127 == neg_mulaw & 127, f'Asymmetric encoding for ±{val}: pos={pos_mulaw:#04x}, neg={neg_mulaw:#04x}'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:359*

### test_roundtrip_preserves_waveform

**Category**: workflow  
**Description**: Workflow: Verify PCM -> mulaw -> PCM round-trip maintains signal quality.  
**Expected**: assert mean_error < 500, f'Mean error too high: {mean_error}'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:391*

### test_roundtrip_known_values

**Category**: workflow  
**Description**: Workflow: Verify round-trip produces expected decoded values.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Verify round-trip produces expected decoded values.'
test_cases = [(0, 0), (32767, 32124), (-32768, -32124), (16000, 15996), (-16000, -15996), (1000, 988), (-1000, -988)]
for original, expected_recovered in test_cases:
    pcm = PcmData(samples=np.array([original], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
    mulaw = pcm_to_mulaw(pcm)
    recovered = mulaw_to_pcm(mulaw).samples[0]
    assert recovered == expected_recovered, f'Round-trip mismatch for PCM {original}: got {recovered}, expected {expected_recovered}'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:424*

### test_snr_acceptable

**Category**: workflow  
**Description**: Workflow: Verify Signal-to-Noise Ratio is acceptable for voice.  
**Expected**: assert snr_db > 35, f'SNR too low: {snr_db:.1f} dB'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:457*

### test_no_clipping_distortion

**Category**: workflow  
**Description**: Workflow: Ensure we don't introduce clipping at signal boundaries.  
**Expected**: assert recovered.samples[3] > 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:498*

### test_pcm_to_mulaw_and_back

**Category**: workflow  
**Description**: Workflow: Test roundtrip conversion preserves audio structure.  
**Expected**: np.testing.assert_array_equal(original_signs, recovered_signs)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:25*

### test_pcm_to_mulaw_resamples

**Category**: workflow  
**Description**: Workflow: Test that pcm_to_mulaw resamples non-8kHz audio.  
**Expected**: assert len(mulaw_bytes) == len(samples) // 2  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that pcm_to_mulaw resamples non-8kHz audio.'
samples = np.sin(np.linspace(0, 2 * np.pi, 160)) * 10000
samples = samples.astype(np.int16)
pcm = PcmData(samples=samples, sample_rate=16000, channels=1, format=AudioFormat.S16)
mulaw_bytes = pcm_to_mulaw(pcm)
assert len(mulaw_bytes) == len(samples) // 2
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:61*

### test_mia_audio_preserves_speech_characteristics

**Category**: workflow  
**Description**: Workflow: Test that mulaw conversion preserves speech-like characteristics.  
**Expected**: assert unique_values > 50, 'Audio should have variation'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: mia_audio_16khz

'Test that mulaw conversion preserves speech-like characteristics.'
mulaw_bytes = pcm_to_mulaw(mia_audio_16khz)
recovered = mulaw_to_pcm(mulaw_bytes)
samples = recovered.samples
assert samples.max() > 1000, 'Audio should have positive peaks'
assert samples.min() < -1000, 'Audio should have negative peaks'
unique_values = len(np.unique(samples))
assert unique_values > 50, 'Audio should have variation'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:89*

### moondream_processor

**Category**: workflow  
**Description**: Workflow: Create and manage MoondreamLocalProcessor lifecycle.  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
'Create and manage MoondreamLocalProcessor lifecycle.'
processor = LocalDetectionProcessor(force_cpu=True)
try:
    yield processor
finally:
    processor.close()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\moondream\tests\test_moondream_local.py:44*

### test_end_call

**Category**: method_call  
**Description**: Test ending a call.  
**Expected**: assert call.ended_at is not None  
**Confidence**: 0.85  

```python
call.end()
assert call.ended_at is not None
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:49*

### test_matches_name

**Category**: method_call  
**Description**: test matches name  
**Expected**: assert response.function_calls[0].name == 'get_weather'  
**Confidence**: 0.85  

```python
response.assert_function_called('get_weather')
assert response.function_calls[0].name == 'get_weather'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:51*

### test_matches_arguments_partial

**Category**: method_call  
**Description**: test matches arguments partial  
**Expected**: assert response.function_calls[0].arguments['limit'] == 10  
**Confidence**: 0.85  

```python
response.assert_function_called('search', arguments={'query': 'hello'})
assert response.function_calls[0].arguments['limit'] == 10
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:63*

### test_wrong_event_type_skips_to_match

**Category**: method_call  
**Description**: test wrong event type skips to match  
**Expected**: assert response.function_calls[0].name == 'search'  
**Confidence**: 0.85  

```python
response.assert_function_called('search')
assert response.function_calls[0].name == 'search'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:90*

### test_none_name_skips_name_check

**Category**: method_call  
**Description**: test none name skips name check  
**Expected**: assert response.function_calls[0].name == 'get_weather'  
**Confidence**: 0.85  

```python
response.assert_function_called()
assert response.function_calls[0].name == 'get_weather'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:100*

### test_matches_among_multiple_calls

**Category**: method_call  
**Description**: test matches among multiple calls  
**Expected**: response.assert_function_called('get_weather', arguments={'location': 'Tokyo'})  
**Confidence**: 0.85  

```python
response.assert_function_called('get_weather', arguments={'location': 'Chicago'})
response.assert_function_called('get_weather', arguments={'location': 'Tokyo'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:110*

### test_matches_among_multiple_calls

**Category**: method_call  
**Description**: test matches among multiple calls  
**Expected**: response.assert_function_called('get_weather', arguments={'location': 'Berlin'})  
**Confidence**: 0.85  

```python
response.assert_function_called('get_weather', arguments={'location': 'Tokyo'})
response.assert_function_called('get_weather', arguments={'location': 'Berlin'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:113*

### test_matches_among_multiple_outputs

**Category**: method_call  
**Description**: test matches among multiple outputs  
**Expected**: response.assert_function_output('get_weather', output={'temp': 30})  
**Confidence**: 0.85  

```python
response.assert_function_output('get_weather', output={'temp': 55})
response.assert_function_output('get_weather', output={'temp': 30})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:161*

### test_matches_among_multiple_outputs

**Category**: method_call  
**Description**: test matches among multiple outputs  
**Expected**: response.assert_function_output('get_weather', output={'temp': 70})  
**Confidence**: 0.85  

```python
response.assert_function_output('get_weather', output={'temp': 30})
response.assert_function_output('get_weather', output={'temp': 70})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:162*

### test_call_then_chat_message

**Category**: method_call  
**Description**: test call then chat message  
**Expected**: assert len(response.chat_messages) == 1  
**Confidence**: 0.85  

```python
response.assert_function_called('get_weather', arguments={'location': 'Tokyo'})
assert len(response.chat_messages) == 1
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:190*

### test_multiple_tool_calls

**Category**: method_call  
**Description**: test multiple tool calls  
**Expected**: assert response.function_calls[1].name == 'get_news'  
**Confidence**: 0.85  

```python
response.assert_function_called('get_weather')
assert response.function_calls[1].name == 'get_news'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_testing\test_eval.py:203*

### test_idle_for

**Category**: method_call  
**Description**: test idle for  
**Expected**: assert conn.idle_since() > 0  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: connection_manager

time.sleep(0.01)
assert conn.idle_since() > 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_edge_transport.py:21*

### test_idle_for

**Category**: method_call  
**Description**: test idle for  
**Expected**: assert conn.idle_since() > 0  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: connection_manager

time.sleep(0.01)
assert conn.idle_since() > 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_edge_transport.py:28*

### test_idle_for

**Category**: method_call  
**Description**: test idle for  
**Expected**: assert not conn.idle_since()  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: connection_manager

time.sleep(0.01)
assert not conn.idle_since()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_edge_transport.py:34*

### test_idle_for

**Category**: method_call  
**Description**: test idle for  
**Expected**: assert conn.idle_since() > 0  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: connection_manager

time.sleep(0.01)
assert conn.idle_since() > 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_edge_transport.py:39*

### test_single_final_event

**Category**: method_call  
**Description**: test single final event  
**Expected**: assert len(buffer) == 1  
**Confidence**: 0.85  

```python
buffer.update('hello')
assert len(buffer) == 1
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:16*

### test_multiple_final_events_create_separate_segments

**Category**: method_call  
**Description**: Each final event (string) creates a new segment.  
**Expected**: assert buffer.segments == ['hello', 'world']  
**Confidence**: 0.85  

```python
buffer.update('world')
assert buffer.segments == ['hello', 'world']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:24*

### test_partial_events_update_last_segment

**Category**: method_call  
**Description**: Partial events update the current working segment.  
**Expected**: assert buffer.segments == ['I']  
**Confidence**: 0.85  

```python
buffer.update(STTPartialTranscriptEvent(text='I'))
assert buffer.segments == ['I']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:30*

### test_partial_events_update_last_segment

**Category**: method_call  
**Description**: Partial events update the current working segment.  
**Expected**: assert buffer.segments == ['I am']  
**Confidence**: 0.85  

```python
buffer.update(STTPartialTranscriptEvent(text='I am'))
assert buffer.segments == ['I am']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:33*

### test_partial_events_update_last_segment

**Category**: method_call  
**Description**: Partial events update the current working segment.  
**Expected**: assert buffer.segments == ['I am walking']  
**Confidence**: 0.85  

```python
buffer.update(STTPartialTranscriptEvent(text='I am walking'))
assert buffer.segments == ['I am walking']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:36*

### test_partial_with_corrections

**Category**: method_call  
**Description**: Partial events can be corrections, not just extensions.  
**Expected**: assert buffer.segments == ['What is the fact']  
**Confidence**: 0.85  

```python
buffer.update(STTPartialTranscriptEvent(text='What is the fact'))
assert buffer.segments == ['What is the fact']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:44*

### test_partial_with_corrections

**Category**: method_call  
**Description**: Partial events can be corrections, not just extensions.  
**Expected**: assert buffer.segments == ['What is the fastest human ability']  
**Confidence**: 0.85  

```python
buffer.update(STTPartialTranscriptEvent(text='What is the fastest human ability'))
assert buffer.segments == ['What is the fastest human ability']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:47*

### test_partial_with_corrections

**Category**: method_call  
**Description**: Partial events can be corrections, not just extensions.  
**Expected**: assert buffer.segments == ['What is the fastest human alive?']  
**Confidence**: 0.85  

```python
buffer.update(STTPartialTranscriptEvent(text='What is the fastest human alive?'))
assert buffer.segments == ['What is the fastest human alive?']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:52*

### test_final_event_finalizes_partial

**Category**: method_call  
**Description**: Final event replaces the partial and finalizes it.  
**Expected**: assert buffer.segments == ['I am walking to the store']  
**Confidence**: 0.85  

```python
buffer.update(STTTranscriptEvent(text='I am walking to the store'))
assert buffer.segments == ['I am walking to the store']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:63*

### test_new_partial_after_final_starts_new_segment

**Category**: method_call  
**Description**: After a final event, new partials start a fresh segment.  
**Expected**: assert buffer.segments == ['Hello there']  
**Confidence**: 0.85  

```python
buffer.update(STTTranscriptEvent(text='Hello there'))
assert buffer.segments == ['Hello there']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_transcript_buffer.py:71*

### test_stop

**Category**: method_call  
**Description**: Test stopping the video track.  
**Expected**: assert track._stopped  
**Confidence**: 0.85  

```python
track.stop()
assert track._stopped
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\decart\tests\test_decart_video_track.py:123*

### test_stop

**Category**: method_call  
**Description**: Test stopping the video track.  
**Expected**: assert track._stopped  
**Confidence**: 0.85  

```python
track.stop()
assert track._stopped
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:45*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate join: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
audio_file_path = os.path.join(os.path.dirname(__file__), 'test_assets/mia.mp3')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:19*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate open: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
container = av.open(audio_file_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:22*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate concatenate: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
samples = np.concatenate(samples)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:49*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate astype: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
samples = samples.astype(np.int16)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:52*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate PcmData: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
pcm = PcmData(samples=samples, sample_rate=target_rate, format=AudioFormat.S16)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:56*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate AudioResampler: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
resampler = av.AudioResampler(format=AudioFormat.S16, layout='mono', rate=target_rate)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:30*

### mia_audio_16khz

**Category**: instantiation  
**Description**: Instantiate mean: mia audio 16khz  
**Confidence**: 0.80  
**Tags**: pytest  

```python
frame_array = np.mean(frame_array, axis=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:45*

### bunny_video_track

**Category**: instantiation  
**Description**: Instantiate join: Create RealVideoTrack from video file  
**Confidence**: 0.80  
**Tags**: pytest  

```python
video_file_path = os.path.join(os.path.dirname(__file__), 'test_assets/bunny_3s.mp4')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:65*

### bunny_video_track

**Category**: instantiation  
**Description**: Instantiate open: Create RealVideoTrack from video file  
**Confidence**: 0.80  
**Tags**: pytest  

```python
self.container = av.open(video_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\base_test.py:72*

### test_even_dimensions_unchanged

**Category**: instantiation  
**Description**: Instantiate _create_frame: Frame with even dimensions should pass through unchanged.  
**Expected**: assert result.width == 100  
**Confidence**: 0.80  

```python
frame = self._create_frame(100, 100)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:28*

### test_even_dimensions_unchanged

**Category**: instantiation  
**Description**: Instantiate ensure_even_dimensions: Frame with even dimensions should pass through unchanged.  
**Expected**: assert result.width == 100  
**Confidence**: 0.80  

```python
result = ensure_even_dimensions(frame)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:29*

### test_both_odd_cropped

**Category**: instantiation  
**Description**: Instantiate _create_frame: Frame with both odd dimensions should be cropped.  
**Expected**: assert result.width == 100  
**Confidence**: 0.80  

```python
frame = self._create_frame(101, 101)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:37*

### test_both_odd_cropped

**Category**: instantiation  
**Description**: Instantiate ensure_even_dimensions: Frame with both odd dimensions should be cropped.  
**Expected**: assert result.width == 100  
**Confidence**: 0.80  

```python
result = ensure_even_dimensions(frame)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:38*

### test_preserves_properties

**Category**: instantiation  
**Description**: Instantiate _create_frame: PTS and time base should be preserved.  
**Expected**: assert result.pts == 12345  
**Confidence**: 0.80  

```python
frame = self._create_frame(101, 100)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:46*

### test_preserves_properties

**Category**: instantiation  
**Description**: Instantiate ensure_even_dimensions: PTS and time base should be preserved.  
**Expected**: assert result.pts == 12345  
**Confidence**: 0.80  

```python
result = ensure_even_dimensions(frame)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:47*

### test_realistic_screen_share_dimensions

**Category**: instantiation  
**Description**: Instantiate _create_frame: Test with realistic odd screen share dimension (1728x1083).  
**Expected**: assert result.width == 1728  
**Confidence**: 0.80  

```python
frame = self._create_frame(1728, 1083)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:55*

### test_realistic_screen_share_dimensions

**Category**: instantiation  
**Description**: Instantiate ensure_even_dimensions: Test with realistic odd screen share dimension (1728x1083).  
**Expected**: assert result.width == 1728  
**Confidence**: 0.80  

```python
result = ensure_even_dimensions(frame)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_video_utils.py:56*

### test_message_initialization

**Category**: instantiation  
**Description**: Instantiate Message: Test that Message initializes correctly with default timestamp.  
**Expected**: assert message.content == 'Hello'  
**Confidence**: 0.80  

```python
message = Message(original={'role': 'user', 'content': 'Hello'}, content='Hello', role='user', user_id='test-user')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_conversation.py:16*

### test_message_custom_id

**Category**: instantiation  
**Description**: Instantiate Message: Test that Message accepts custom ID.  
**Expected**: assert message.id == 'custom-id-123'  
**Confidence**: 0.80  

```python
message = Message(content='Hello', role='user', user_id='test-user', id='custom-id-123')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_conversation.py:32*

### test_create_call

**Category**: instantiation  
**Description**: Instantiate CallWebhookInput: Test creating a TwilioCall.  
**Expected**: assert call.call_sid == 'CA123456'  
**Confidence**: 0.80  

```python
webhook_data = CallWebhookInput(CallSid='CA123456', AccountSid='AC123', CallStatus='ringing', Direction='inbound', From='+1234567890', Caller='+1234567890', CallerCity='New York', To='+0987654321', Called='+0987654321')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:22*

### test_create_call

**Category**: instantiation  
**Description**: Instantiate TwilioCall: Test creating a TwilioCall.  
**Expected**: assert call.call_sid == 'CA123456'  
**Confidence**: 0.80  

```python
call = twilio.TwilioCall(call_sid='CA123456', webhook_data=webhook_data)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:33*

### test_end_call

**Category**: instantiation  
**Description**: Instantiate TwilioCall: Test ending a call.  
**Expected**: assert call.ended_at is None  
**Confidence**: 0.80  

```python
call = twilio.TwilioCall(call_sid='CA123456')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:46*

### test_create_and_get

**Category**: instantiation  
**Description**: Instantiate CallWebhookInput: Test creating and retrieving calls.  
**Expected**: assert call.call_sid == 'CA123'  
**Confidence**: 0.80  

```python
webhook_data = CallWebhookInput(CallSid='CA123', AccountSid='AC123', CallStatus='ringing', Direction='inbound', From='+123', Caller='+123', To='+456', Called='+456')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:58*

### test_create_and_get

**Category**: instantiation  
**Description**: Instantiate create: Test creating and retrieving calls.  
**Expected**: assert call.call_sid == 'CA123'  
**Confidence**: 0.80  

```python
call = registry.create('CA123', webhook_data=webhook_data)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:69*

### test_create_and_get

**Category**: instantiation  
**Description**: Instantiate get: Test creating and retrieving calls.  
**Expected**: assert retrieved is call  
**Confidence**: 0.80  

```python
retrieved = registry.get('CA123')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:73*

### test_remove

**Category**: instantiation  
**Description**: Instantiate remove: Test removing a call.  
**Expected**: assert removed is not None  
**Confidence**: 0.80  

```python
removed = registry.remove('CA123')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:86*

### test_mulaw_to_pcm

**Category**: instantiation  
**Description**: Instantiate bytes: Test mulaw to PCM conversion.  
**Expected**: assert pcm.sample_rate == 8000  
**Confidence**: 0.80  

```python
mulaw_bytes = bytes([255, 127, 0, 128])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_twilio.py:110*

### test_to_dict_some_fields_success

**Category**: instantiation  
**Description**: Instantiate to_dict: test to dict some fields success  
**Expected**: assert set(some_fields) == set(metrics_dict.keys())  
**Confidence**: 0.80  

```python
metrics_dict = metrics.to_dict(fields=some_fields)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_observability.py:431*

### test_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test message  
**Expected**: assert isinstance(messages[0], Message)  
**Confidence**: 0.80  

```python
messages = OpenAILLM._normalize_message('say hi')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\openai\tests\test_openai_llm.py:19*

### test_advanced_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test advanced message  
**Expected**: assert messages2[0].original is not None  
**Confidence**: 0.80  

```python
messages2 = OpenAILLM._normalize_message(advanced)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\openai\tests\test_openai_llm.py:37*

### test_idle_for

**Category**: instantiation  
**Description**: Instantiate StreamConnection: test idle for  
**Expected**: assert conn.idle_since() > 0  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: connection_manager

conn = StreamConnection(connection=connection_manager)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_edge_transport.py:20*

### test_idle_for

**Category**: instantiation  
**Description**: Instantiate Participant: test idle for  
**Expected**: assert not conn.idle_since()  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: connection_manager

another_participant = Participant(user_id='another-user-id')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_edge_transport.py:32*

### test_init_with_agent_image_url_instead_of_id

**Category**: instantiation  
**Description**: Instantiate _make_publisher: test init with agent image url instead of id  
**Expected**: assert pub._client._agent_image_url == 'https://example.com/img.png'  
**Confidence**: 0.80  

```python
pub = _make_publisher(agent_id=None, agent_image_url='https://example.com/img.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\lemonslice\tests\test_lemonslice_plugin.py:37*

### test_init_custom_resolution

**Category**: instantiation  
**Description**: Instantiate _make_publisher: test init custom resolution  
**Expected**: assert isinstance(track, QueuedVideoTrack)  
**Confidence**: 0.80  

```python
pub = _make_publisher(width=640, height=480)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\lemonslice\tests\test_lemonslice_plugin.py:63*

### test_audio_queue_initialization

**Category**: instantiation  
**Description**: Instantiate AudioQueue: Test that AudioQueue initializes correctly.  
**Expected**: assert queue.buffer_limit_ms == 1000  
**Confidence**: 0.80  

```python
queue = AudioQueue(buffer_limit_ms=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_audio_queue.py:15*

### test_audio_queue_initialization

**Category**: instantiation  
**Description**: Instantiate AudioQueue: Test that AudioQueue initializes correctly.  
**Expected**: assert queue.buffer_limit_ms == 1000  
**Confidence**: 0.80  

```python
queue = AudioQueue(buffer_limit_ms=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_audio_queue.py:15*

### conversation

**Category**: instantiation  
**Description**: Instantiate StreamConversation: Create a StreamConversation with small chunk size for testing.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
conversation = StreamConversation(instructions='Test', messages=[], channel=mock_channel, chunk_size=50)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:22*

### test_no_chunking_needed

**Category**: instantiation  
**Description**: Instantiate _smart_chunk: Test that small messages aren't chunked.  
**Expected**: assert len(chunks) == 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

chunks = conversation._smart_chunk(text, 50)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:33*

### test_simple_chunking

**Category**: instantiation  
**Description**: Instantiate _smart_chunk: Test basic chunking at line boundaries.  
**Expected**: assert len(chunks) > 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

chunks = conversation._smart_chunk(text, 30)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:41*

### test_simple_chunking

**Category**: instantiation  
**Description**: Instantiate join: Test basic chunking at line boundaries.  
**Expected**: assert reconstructed.replace('\n\n', '\n').strip() == text.strip()  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

reconstructed = '\n'.join(chunks)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:47*

### test_code_block_not_split

**Category**: instantiation  
**Description**: Instantiate _smart_chunk: Test that code blocks stay together.  
**Expected**: assert has_complete_code_block, 'Code block was split incorrectly'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

chunks = conversation._smart_chunk(text, 100)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:62*

### test_code_block_not_split

**Category**: instantiation  
**Description**: Instantiate any: Test that code blocks stay together.  
**Expected**: assert has_complete_code_block, 'Code block was split incorrectly'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

has_complete_code_block = any(('```python' in chunk and 'return "world"' in chunk and ('```' in chunk) for chunk in chunks))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:65*

### test_code_block_in_own_chunk

**Category**: instantiation  
**Description**: Instantiate _smart_chunk: Test that large code blocks get their own chunk.  
**Expected**: assert len(chunks) >= 2  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

chunks = conversation._smart_chunk(text, 60)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:85*

### test_code_block_in_own_chunk

**Category**: instantiation  
**Description**: Instantiate next: Test that large code blocks get their own chunk.  
**Expected**: assert code_chunk is not None  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

code_chunk = next((c for c in chunks if '```python' in c), None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:91*

### test_very_large_code_block_split

**Category**: instantiation  
**Description**: Instantiate _smart_chunk: Test that code blocks larger than max_size are split at newlines.  
**Expected**: assert len(chunks) > 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

chunks = conversation._smart_chunk(text, 80)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:101*

### test_paragraph_chunking

**Category**: instantiation  
**Description**: Instantiate _smart_chunk: Test chunking at paragraph boundaries.  
**Expected**: assert len(chunks) >= 2  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: conversation

chunks = conversation._smart_chunk(text, 40)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_message_chunking.py:114*

### test_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test message  
**Expected**: assert isinstance(messages[0], Message)  
**Confidence**: 0.80  

```python
messages = XAILLM._normalize_message('say hi')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\xai\tests\test_xai_llm.py:16*

### sample_frame_large

**Category**: instantiation  
**Description**: Instantiate new: Test av.VideoFrame fixture with different size.  
**Confidence**: 0.80  
**Tags**: pytest  

```python
image = Image.new('RGB', (1920, 1080), color='red')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\decart\tests\test_decart_video_track.py:25*

### test_init_custom_dimensions

**Category**: instantiation  
**Description**: Instantiate DecartVideoTrack: Test initialization with custom dimensions.  
**Expected**: assert track.width == 1920  
**Confidence**: 0.80  

```python
track = DecartVideoTrack(width=1920, height=1080)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\decart\tests\test_decart_video_track.py:42*

### test_parse_success

**Category**: instantiation  
**Description**: Instantiate Instructions: test parse success  
**Expected**: assert instructions.input_text == input_text  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: tmp_path, input_text, file_data, full_reference

instructions = Instructions(input_text=input_text, base_dir=tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_instructions.py:23*

### test_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: Test basic message normalization.  
**Expected**: assert isinstance(messages[0], Message)  
**Confidence**: 0.80  

```python
messages = LLM._normalize_message('say hi')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\openrouter\tests\test_openrouter_llm.py:32*

### test_advanced_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: Test advanced message format with image.  
**Expected**: assert messages[0].original is not None  
**Confidence**: 0.80  

```python
messages = LLM._normalize_message(advanced)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\openrouter\tests\test_openrouter_llm.py:51*

### test_merge_messages_identical_consecutive_collapses

**Category**: instantiation  
**Description**: Instantiate _merge_messages: test merge messages identical consecutive collapses  
**Expected**: assert len(result) == 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: llm

result = llm._merge_messages(messages)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\anthropic\tests\test_anthropic_llm.py:105*

### test_merge_messages_different_content_produces_blocks

**Category**: instantiation  
**Description**: Instantiate _merge_messages: test merge messages different content produces blocks  
**Expected**: assert len(result) == 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: llm

result = llm._merge_messages(messages)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\anthropic\tests\test_anthropic_llm.py:114*

### test_merge_messages_list_content_merges

**Category**: instantiation  
**Description**: Instantiate _merge_messages: test merge messages list content merges  
**Expected**: assert len(result) == 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: llm

result = llm._merge_messages(messages)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\anthropic\tests\test_anthropic_llm.py:127*

### test_normalize_message_string_content

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test normalize message string content  
**Expected**: assert len(messages) == 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: llm

messages = ClaudeLLM._normalize_message({'role': 'user', 'content': 'hello'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\anthropic\tests\test_anthropic_llm.py:138*

### test_normalize_message_list_content_stringified

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test normalize message list content stringified  
**Expected**: assert len(messages) == 1  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: llm

messages = ClaudeLLM._normalize_message({'role': 'assistant', 'content': [{'type': 'text', 'text': 'hello'}, {'type': 'text', 'text': 'world'}]})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\anthropic\tests\test_anthropic_llm.py:144*

### mock_channel

**Category**: instantiation  
**Description**: Instantiate AsyncMock: Create a mock Channel.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
channel.send_message = AsyncMock(return_value=mock_response)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_conversation.py:48*

### stream_conversation

**Category**: instantiation  
**Description**: Instantiate StreamConversation: Create a StreamConversation instance with mocked dependencies.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: mock_channel

conversation = StreamConversation(instructions=instructions, messages=messages, channel=mock_channel)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\getstream\tests\test_stream_conversation.py:57*

### test_decode_silence

**Category**: instantiation  
**Description**: Instantiate mulaw_to_pcm: Mulaw 0xFF and 0x7F represent silence (near zero).  
**Expected**: assert pcm.samples[0] == 0  
**Confidence**: 0.80  

```python
pcm = mulaw_to_pcm(bytes([255]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:305*

### test_decode_silence

**Category**: instantiation  
**Description**: Instantiate mulaw_to_pcm: Mulaw 0xFF and 0x7F represent silence (near zero).  
**Expected**: assert pcm.samples[0] == 0  
**Confidence**: 0.80  

```python
pcm = mulaw_to_pcm(bytes([127]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:308*

### test_decode_matches_reference

**Category**: instantiation  
**Description**: Instantiate bytes: Compare our decoder against ITU-T G.711 reference values.  
**Confidence**: 0.80  

```python
mulaw_bytes = bytes([mulaw_val])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:314*

### test_decode_matches_reference

**Category**: instantiation  
**Description**: Instantiate mulaw_to_pcm: Compare our decoder against ITU-T G.711 reference values.  
**Confidence**: 0.80  

```python
our_pcm = mulaw_to_pcm(mulaw_bytes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:315*

### test_encode_silence

**Category**: instantiation  
**Description**: Instantiate PcmData: Zero PCM should encode to mulaw silence.  
**Expected**: assert mulaw[0] == 255  
**Confidence**: 0.80  

```python
pcm = PcmData(samples=np.array([0], dtype=np.int16), sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\twilio\tests\test_audio.py:330*

### mock_video_track

**Category**: instantiation  
**Description**: Instantiate MagicMock: Mock video track.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
track = MagicMock(spec=MediaStreamTrack)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\decart\tests\test_decart_restyling.py:19*

### sample_frame

**Category**: instantiation  
**Description**: Instantiate new: Test av.VideoFrame fixture.  
**Confidence**: 0.80  
**Tags**: pytest  

```python
image = Image.new('RGB', (1280, 720), color='blue')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\decart\tests\test_decart_restyling.py:28*

### test_pcm_to_mulaw_and_back

**Category**: instantiation  
**Description**: Instantiate array: Test roundtrip conversion preserves audio structure.  
**Expected**: assert recovered.sample_rate == TWILIO_SAMPLE_RATE  
**Confidence**: 0.80  

```python
samples = np.array([100, 1000, -1000, 16000, -16000, 32000, -32000], dtype=np.int16)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:28*

### test_pcm_to_mulaw_and_back

**Category**: instantiation  
**Description**: Instantiate PcmData: Test roundtrip conversion preserves audio structure.  
**Expected**: assert recovered.sample_rate == TWILIO_SAMPLE_RATE  
**Confidence**: 0.80  

```python
pcm = PcmData(samples=samples, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:31*

### test_pcm_to_mulaw_and_back

**Category**: instantiation  
**Description**: Instantiate pcm_to_mulaw: Test roundtrip conversion preserves audio structure.  
**Expected**: assert recovered.sample_rate == TWILIO_SAMPLE_RATE  
**Confidence**: 0.80  

```python
mulaw_bytes = pcm_to_mulaw(pcm)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:38*

### test_pcm_to_mulaw_and_back

**Category**: instantiation  
**Description**: Instantiate mulaw_to_pcm: Test roundtrip conversion preserves audio structure.  
**Expected**: assert recovered.sample_rate == TWILIO_SAMPLE_RATE  
**Confidence**: 0.80  

```python
recovered = mulaw_to_pcm(mulaw_bytes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:39*

### test_pcm_to_mulaw_and_back

**Category**: instantiation  
**Description**: Instantiate sign: Test roundtrip conversion preserves audio structure.  
**Expected**: np.testing.assert_array_equal(original_signs, recovered_signs)  
**Confidence**: 0.80  

```python
original_signs = np.sign(samples)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:46*

### test_pcm_to_mulaw_and_back

**Category**: instantiation  
**Description**: Instantiate sign: Test roundtrip conversion preserves audio structure.  
**Expected**: np.testing.assert_array_equal(original_signs, recovered_signs)  
**Confidence**: 0.80  

```python
recovered_signs = np.sign(recovered.samples)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:47*

### test_mulaw_to_pcm_output_format

**Category**: instantiation  
**Description**: Instantiate bytes: Test mulaw_to_pcm returns correct format.  
**Expected**: assert pcm.sample_rate == TWILIO_SAMPLE_RATE  
**Confidence**: 0.80  

```python
mulaw_bytes = bytes([255, 255, 255, 255])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_mulaw_conversion.py:53*

### moondream_processor

**Category**: instantiation  
**Description**: Instantiate LocalDetectionProcessor: Create and manage MoondreamLocalProcessor lifecycle.  
**Confidence**: 0.80  
**Tags**: pytest  

```python
processor = LocalDetectionProcessor(force_cpu=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\moondream\tests\test_moondream_local.py:46*

### test_device_mps_converted_to_cpu

**Category**: instantiation  
**Description**: Instantiate LocalDetectionProcessor: Test MPS override to CPU (moondream doesn't work with MPS).  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

processor2 = LocalDetectionProcessor(force_cpu=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\moondream\tests\test_moondream_local.py:268*

### test_device_explicit_cpu

**Category**: instantiation  
**Description**: Instantiate LocalDetectionProcessor: Test explicit CPU device selection.  
**Confidence**: 0.80  

```python
processor = LocalDetectionProcessor(force_cpu=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\moondream\tests\test_moondream_local.py:277*

### test_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test message  
**Expected**: assert isinstance(messages[0], Message)  
**Confidence**: 0.80  

```python
messages = GeminiLLM._normalize_message('say hi')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\gemini\tests\test_gemini_llm.py:16*

### test_advanced_message

**Category**: instantiation  
**Description**: Instantiate _normalize_message: test advanced message  
**Expected**: assert messages2[0].original is not None  
**Confidence**: 0.80  

```python
messages2 = GeminiLLM._normalize_message(advanced)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\gemini\tests\test_gemini_llm.py:24*

### test_call_function

**Category**: instantiation  
**Description**: Instantiate call_function: Test calling a registered function.  
**Expected**: assert result == 8  
**Confidence**: 0.80  

```python
result = registry.call_function('add_numbers', {'a': 5, 'b': 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_function_calling.py:40*

### test_call_function_with_defaults

**Category**: instantiation  
**Description**: Instantiate call_function: Test calling a function with default parameters.  
**Expected**: assert result == 8  
**Confidence**: 0.80  

```python
result = registry.call_function('test_func', {'x': 5, 'y': 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_function_calling.py:53*

### test_call_function_with_defaults

**Category**: instantiation  
**Description**: Instantiate call_function: Test calling a function with default parameters.  
**Expected**: assert result == 15  
**Confidence**: 0.80  

```python
result = registry.call_function('test_func', {'x': 5})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_function_calling.py:57*

### test_get_callable

**Category**: instantiation  
**Description**: Instantiate get_callable: Test getting callable function.  
**Expected**: assert callable_func(5) == 10  
**Confidence**: 0.80  

```python
callable_func = registry.get_callable('test_func')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_function_calling.py:103*

### test_global_registry

**Category**: instantiation  
**Description**: Instantiate call_function: Test that the global registry works.  
**Expected**: assert result == 12  
**Confidence**: 0.80  

```python
result = function_registry.call_function('global_test_func', {'x': 4})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\tests\test_function_calling.py:124*

### test_custom_environment

**Category**: instantiation  
**Description**: Instantiate ComputerUse: Test ComputerUse with custom environment.  
**Expected**: assert result.computer_use.environment == types.Environment.ENVIRONMENT_BROWSER  
**Confidence**: 0.80  

```python
tool = tools.ComputerUse(environment=types.Environment.ENVIRONMENT_BROWSER)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\gemini\tests\test_gemini_tools.py:71*

### test_to_tool_with_created_store

**Category**: instantiation  
**Description**: Instantiate Tool: Test FileSearch converts to Tool when store is created.  
**Expected**: assert isinstance(result, types.Tool)  
**Confidence**: 0.80  
**Tags**: mock  

```python
mock_store.get_tool.return_value = types.Tool(file_search=types.FileSearch(file_search_store_names=['test-store']))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\gemini\tests\test_gemini_tools.py:85*

### test_to_tool_with_created_store

**Category**: instantiation  
**Description**: Instantiate FileSearch: Test FileSearch converts to Tool when store is created.  
**Expected**: assert isinstance(result, types.Tool)  
**Confidence**: 0.80  
**Tags**: mock  

```python
tool = tools.FileSearch(mock_store)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\gemini\tests\test_gemini_tools.py:89*

### test_to_tool_raises_when_store_not_created

**Category**: instantiation  
**Description**: Instantiate FileSearch: Test FileSearch raises error when store is not created.  
**Confidence**: 0.80  
**Tags**: mock  

```python
tool = tools.FileSearch(mock_store)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\gemini\tests\test_gemini_tools.py:101*

### test_init_with_api_key

**Category**: instantiation  
**Description**: Instantiate HeyGenSession: Test initialization with explicit API key.  
**Expected**: assert session.avatar_id == 'test_avatar'  
**Confidence**: 0.80  

```python
session = HeyGenSession(avatar_id='test_avatar', quality=VideoQuality.HIGH, api_key='test_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:14*

### test_init

**Category**: instantiation  
**Description**: Instantiate HeyGenVideoTrack: Test video track initialization.  
**Expected**: assert track.width == 1920  
**Confidence**: 0.80  

```python
track = HeyGenVideoTrack(width=1920, height=1080)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:36*

### test_init

**Category**: instantiation  
**Description**: Instantiate HeyGenRTCManager: Test RTC manager initialization.  
**Confidence**: 0.80  
**Tags**: mock  

```python
manager = HeyGenRTCManager(avatar_id='test_avatar', quality=VideoQuality.MEDIUM, api_key='test_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:56*

### test_is_connected_property

**Category**: instantiation  
**Description**: Instantiate HeyGenRTCManager: Test is_connected property.  
**Confidence**: 0.80  
**Tags**: mock  

```python
manager = HeyGenRTCManager(api_key='test_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:68*

### test_init

**Category**: instantiation  
**Description**: Instantiate AvatarPublisher: Test avatar publisher initialization.  
**Confidence**: 0.80  
**Tags**: mock  

```python
publisher = AvatarPublisher(avatar_id='test_avatar', quality=VideoQuality.HIGH, resolution=(1920, 1080), api_key='test_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:82*

### test_publish_video_track

**Category**: instantiation  
**Description**: Instantiate AvatarPublisher: Test publishing video track.  
**Confidence**: 0.80  
**Tags**: mock  

```python
publisher = AvatarPublisher(api_key='test_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-Vision-Agents-3fea6ac4\plugins\heygen\tests\test_heygen_plugin.py:97*

