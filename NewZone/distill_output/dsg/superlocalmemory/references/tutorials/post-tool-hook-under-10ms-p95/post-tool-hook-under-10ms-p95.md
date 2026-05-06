# How To: Post Tool Hook Under 10Ms P95

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Hot-path p95 < 10 ms over 100 no-op invocations (I1 budget).

No matching pending row → no DB write → pure read + early-return.
That is the representative hot-path case (no recall happened).

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

### Step 1: 'Hot-path p95 < 10 ms over 100 no-op invocations (I1 budget).\n\n    No matching pending row → no DB write → pure read + early-return.\n    That is the representative hot-path case (no recall happened).\n    '

```python
'Hot-path p95 < 10 ms over 100 no-op invocations (I1 budget).\n\n    No matching pending row → no DB write → pure read + early-return.\n    That is the representative hot-path case (no recall happened).\n    '
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Assign payload = value

```python
payload = {'session_id': 'sess-none', 'tool_name': 'Read', 'tool_response': 'no markers here'}
```

**Verification:**
```python
assert p95_ms < 30.0, f'post_tool_hook p95 = {p95_ms:.2f}ms > 30ms'
```

### Step 3: Assign durations = value

```python
durations = []
```

### Step 4: Call durations.sort()

```python
durations.sort()
```

### Step 5: Assign p95_ms = value

```python
p95_ms = durations[94] / 1000000.0
```

**Verification:**
```python
assert p95_ms < 30.0, f'post_tool_hook p95 = {p95_ms:.2f}ms > 30ms'
```

### Step 6: Call _invoke_hook()

```python
_invoke_hook(h.main, payload, monkeypatch)
```

### Step 7: Assign t0 = time.perf_counter_ns(...)

```python
t0 = time.perf_counter_ns()
```

### Step 8: Assign unknown = _invoke_hook(...)

```python
rc, _ = _invoke_hook(h.main, payload, monkeypatch)
```

### Step 9: Call durations.append()

```python
durations.append(time.perf_counter_ns() - t0)
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
'Hot-path p95 < 10 ms over 100 no-op invocations (I1 budget).\n\n    No matching pending row → no DB write → pure read + early-return.\n    That is the representative hot-path case (no recall happened).\n    '
from superlocalmemory.hooks import post_tool_outcome_hook as h
payload = {'session_id': 'sess-none', 'tool_name': 'Read', 'tool_response': 'no markers here'}
for _ in range(5):
    _invoke_hook(h.main, payload, monkeypatch)
durations = []
for _ in range(100):
    t0 = time.perf_counter_ns()
    rc, _ = _invoke_hook(h.main, payload, monkeypatch)
    durations.append(time.perf_counter_ns() - t0)
    assert rc == 0
durations.sort()
p95_ms = durations[94] / 1000000.0
assert p95_ms < 30.0, f'post_tool_hook p95 = {p95_ms:.2f}ms > 30ms'
```

## Next Steps


---

*Source: test_outcome_hooks.py:322 | Complexity: Advanced | Last updated: 2026-05-05*