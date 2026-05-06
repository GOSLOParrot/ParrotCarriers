# How To: Sec M4 Perf Log Entry Is Valid Ndjson

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test sec m4 perf log entry is valid ndjson

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
assert rec['hook'] == 'stage8_nd'
```

### Step 2: Assign oc._PERF_LOG_FD = None

```python
oc._PERF_LOG_FD = None
```

**Verification:**
```python
assert rec['outcome'] == 'ok'
```

### Step 3: Assign oc._PERF_LOG_PATH = None

```python
oc._PERF_LOG_PATH = None
```

### Step 4: Assign oc._PERF_LOG_WRITE_COUNT = 0

```python
oc._PERF_LOG_WRITE_COUNT = 0
```

### Step 5: Call oc.log_perf()

```python
oc.log_perf('stage8_nd', 0.5, 'ok')
```

### Step 6: Assign line = value

```python
line = oc.perf_log_path().read_text(encoding='utf-8').splitlines()[-1]
```

### Step 7: Assign rec = json.loads(...)

```python
rec = json.loads(line)
```

**Verification:**
```python
assert rec['hook'] == 'stage8_nd'
```

### Step 8: Call oc._PERF_LOG_FD.flush()

```python
oc._PERF_LOG_FD.flush()
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
oc.log_perf('stage8_nd', 0.5, 'ok')
if oc._PERF_LOG_FD is not None:
    oc._PERF_LOG_FD.flush()
line = oc.perf_log_path().read_text(encoding='utf-8').splitlines()[-1]
rec = json.loads(line)
assert rec['hook'] == 'stage8_nd'
assert rec['outcome'] == 'ok'
```

## Next Steps


---

*Source: test_stage8_outcome_common_security.py:92 | Complexity: Advanced | Last updated: 2026-05-05*