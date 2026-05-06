# How To: Sec M4 Perf Log Rotates Over Cap

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test sec m4 perf log rotates over cap

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `stat`
- `sys`
- `pathlib`
- `pytest`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Call monkeypatch.setenv()

```python
monkeypatch.setenv('SLM_HOME', str(tmp_path / 'slm'))
```

**Verification:**
```python
assert rotated.exists(), 'rotation did not produce hook-perf.log.1'
```

### Step 2: Assign oc._PERF_LOG_FD = None

```python
oc._PERF_LOG_FD = None
```

**Verification:**
```python
assert log_path.exists()
```

### Step 3: Assign oc._PERF_LOG_PATH = None

```python
oc._PERF_LOG_PATH = None
```

### Step 4: Assign oc._PERF_LOG_WRITE_COUNT = 0

```python
oc._PERF_LOG_WRITE_COUNT = 0
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(oc, 'PERF_LOG_MAX_BYTES', 1024, raising=True)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr(oc, 'PERF_LOG_CHECK_EVERY', 4, raising=True)
```

### Step 7: Assign log_path = oc.perf_log_path(...)

```python
log_path = oc.perf_log_path()
```

### Step 8: Assign rotated = log_path.with_suffix(...)

```python
rotated = log_path.with_suffix(log_path.suffix + '.1')
```

**Verification:**
```python
assert rotated.exists(), 'rotation did not produce hook-perf.log.1'
```

### Step 9: Call oc.log_perf()

```python
oc.log_perf('stage8', 1.234, f'outcome_{i}')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
monkeypatch.setenv('SLM_HOME', str(tmp_path / 'slm'))
from superlocalmemory.hooks import _outcome_common as oc
oc._PERF_LOG_FD = None
oc._PERF_LOG_PATH = None
oc._PERF_LOG_WRITE_COUNT = 0
monkeypatch.setattr(oc, 'PERF_LOG_MAX_BYTES', 1024, raising=True)
monkeypatch.setattr(oc, 'PERF_LOG_CHECK_EVERY', 4, raising=True)
log_path = oc.perf_log_path()
for i in range(200):
    oc.log_perf('stage8', 1.234, f'outcome_{i}')
rotated = log_path.with_suffix(log_path.suffix + '.1')
assert rotated.exists(), 'rotation did not produce hook-perf.log.1'
assert log_path.exists()
```

## Next Steps


---

*Source: test_stage8_outcome_common_security.py:66 | Complexity: Advanced | Last updated: 2026-05-05*