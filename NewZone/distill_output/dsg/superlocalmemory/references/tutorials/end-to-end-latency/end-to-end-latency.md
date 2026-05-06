# How To: End To End Latency

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Full store + recall cycle completes within 10 seconds per question.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `time`
- `pathlib`
- `typing`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.llm.backbone`
- `superlocalmemory.storage.models`
- `httpx`
- `httpx`
- `httpx`
- `warnings`

**Setup Required:**
```python
# Fixtures: mode_b_engine
```

## Step-by-Step Guide

### Step 1: 'Full store + recall cycle completes within 10 seconds per question.'

```python
'Full store + recall cycle completes within 10 seconds per question.'
```

**Verification:**
```python
assert total_ms < 30000, f'Store+recall took {total_ms:.0f}ms (>{30000}ms limit). Store: {store_ms:.0f}ms, Recall: {recall_ms:.0f}ms'
```

### Step 2: Assign t0 = time.perf_counter(...)

```python
t0 = time.perf_counter()
```

**Verification:**
```python
assert len(response.results) > 0, 'Recall returned zero results'
```

### Step 3: Call mode_b_engine.store()

```python
mode_b_engine.store('Charlie is an architect at Amazon in Seattle.', session_id='lat_s1')
```

### Step 4: Assign store_ms = value

```python
store_ms = (time.perf_counter() - t0) * 1000
```

### Step 5: Assign t1 = time.perf_counter(...)

```python
t1 = time.perf_counter()
```

### Step 6: Assign response = mode_b_engine.recall(...)

```python
response = mode_b_engine.recall('What does Charlie do?')
```

### Step 7: Assign recall_ms = value

```python
recall_ms = (time.perf_counter() - t1) * 1000
```

### Step 8: Assign total_ms = value

```python
total_ms = store_ms + recall_ms
```

**Verification:**
```python
assert total_ms < 30000, f'Store+recall took {total_ms:.0f}ms (>{30000}ms limit). Store: {store_ms:.0f}ms, Recall: {recall_ms:.0f}ms'
```


## Complete Example

```python
# Setup
# Fixtures: mode_b_engine

# Workflow
'Full store + recall cycle completes within 10 seconds per question.'
t0 = time.perf_counter()
mode_b_engine.store('Charlie is an architect at Amazon in Seattle.', session_id='lat_s1')
store_ms = (time.perf_counter() - t0) * 1000
t1 = time.perf_counter()
response = mode_b_engine.recall('What does Charlie do?')
recall_ms = (time.perf_counter() - t1) * 1000
total_ms = store_ms + recall_ms
assert total_ms < 30000, f'Store+recall took {total_ms:.0f}ms (>{30000}ms limit). Store: {store_ms:.0f}ms, Recall: {recall_ms:.0f}ms'
assert len(response.results) > 0, 'Recall returned zero results'
```

## Next Steps


---

*Source: test_mode_b_ollama.py:537 | Complexity: Advanced | Last updated: 2026-05-05*