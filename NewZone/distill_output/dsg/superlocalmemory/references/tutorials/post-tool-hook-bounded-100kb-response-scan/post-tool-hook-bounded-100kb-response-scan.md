# How To: Post Tool Hook Bounded 100Kb Response Scan

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: 10 MB tool_response truncated to <=100KB before scan (perf bound).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `os`
- `sqlite3`
- `statistics`
- `sys`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.recall_pipeline`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.core.topic_signature`
- `superlocalmemory.hooks`
- `superlocalmemory.core.topic_signature`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.learning`
- `superlocalmemory.hooks`
- `sqlite3`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`

**Setup Required:**
```python
# Fixtures: memory_db, slm_home, install_token, monkeypatch
```

## Step-by-Step Guide

### Step 1: '10 MB tool_response truncated to <=100KB before scan (perf bound).'

```python
'10 MB tool_response truncated to <=100KB before scan (perf bound).'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-big', session_id='sess-A', fact_ids=['fact-99'])
```

**Verification:**
```python
assert out == '{}'
```

### Step 3: Assign marker = _make_marker(...)

```python
marker = _make_marker('fact-99')
```

**Verification:**
```python
assert elapsed < 0.2, f'scan took {elapsed * 1000:.1f}ms, expected <200ms'
```

### Step 4: Assign big = value

```python
big = 'x' * (2 * 1024 * 1024) + marker
```

### Step 5: Assign payload = value

```python
payload = {'session_id': 'sess-A', 'tool_name': 'Read', 'tool_response': marker + big}
```

### Step 6: Assign t0 = time.monotonic(...)

```python
t0 = time.monotonic()
```

### Step 7: Assign unknown = _invoke_hook(...)

```python
rc, out = _invoke_hook(h.main, payload, monkeypatch)
```

### Step 8: Assign elapsed = value

```python
elapsed = time.monotonic() - t0
```

**Verification:**
```python
assert rc == 0
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, slm_home, install_token, monkeypatch

# Workflow
'10 MB tool_response truncated to <=100KB before scan (perf bound).'
from superlocalmemory.hooks import post_tool_outcome_hook as h
_seed_pending(memory_db, outcome_id='oid-big', session_id='sess-A', fact_ids=['fact-99'])
marker = _make_marker('fact-99')
big = 'x' * (2 * 1024 * 1024) + marker
payload = {'session_id': 'sess-A', 'tool_name': 'Read', 'tool_response': marker + big}
t0 = time.monotonic()
rc, out = _invoke_hook(h.main, payload, monkeypatch)
elapsed = time.monotonic() - t0
assert rc == 0
assert out == '{}'
assert elapsed < 0.2, f'scan took {elapsed * 1000:.1f}ms, expected <200ms'
```

## Next Steps


---

*Source: test_outcome_hooks.py:241 | Complexity: Advanced | Last updated: 2026-05-05*