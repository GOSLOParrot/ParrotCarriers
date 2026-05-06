# How To: Hook Perf Log Shape

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: hook-perf.log lines must be NDJSON with {ts, hook, duration_ms, outcome}.

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

### Step 1: 'hook-perf.log lines must be NDJSON with {ts, hook, duration_ms, outcome}.'

```python
'hook-perf.log lines must be NDJSON with {ts, hook, duration_ms, outcome}.'
```

**Verification:**
```python
assert log.exists(), 'hook-perf.log not written'
```

### Step 2: Assign payload = value

```python
payload = {'session_id': 'sess-perf', 'tool_name': 'Read', 'tool_response': 'no markers'}
```

**Verification:**
```python
assert field in obj, f'missing {field!r} in perf log: {obj}'
```

### Step 3: Call _invoke_hook()

```python
_invoke_hook(h.main, payload, monkeypatch)
```

**Verification:**
```python
assert isinstance(obj['ts'], (int, float))
```

### Step 4: Assign log = value

```python
log = slm_home / 'logs' / 'hook-perf.log'
```

**Verification:**
```python
assert isinstance(obj['hook'], str)
```

### Step 5: Assign line = value

```python
line = log.read_text().strip().splitlines()[-1]
```

**Verification:**
```python
assert isinstance(obj['duration_ms'], (int, float))
```

### Step 6: Assign obj = json.loads(...)

```python
obj = json.loads(line)
```

**Verification:**
```python
assert isinstance(obj['outcome'], str)
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, slm_home, install_token, monkeypatch

# Workflow
'hook-perf.log lines must be NDJSON with {ts, hook, duration_ms, outcome}.'
from superlocalmemory.hooks import post_tool_outcome_hook as h
payload = {'session_id': 'sess-perf', 'tool_name': 'Read', 'tool_response': 'no markers'}
_invoke_hook(h.main, payload, monkeypatch)
log = slm_home / 'logs' / 'hook-perf.log'
assert log.exists(), 'hook-perf.log not written'
line = log.read_text().strip().splitlines()[-1]
obj = json.loads(line)
for field in ('ts', 'hook', 'duration_ms', 'outcome'):
    assert field in obj, f'missing {field!r} in perf log: {obj}'
assert isinstance(obj['ts'], (int, float))
assert isinstance(obj['hook'], str)
assert isinstance(obj['duration_ms'], (int, float))
assert isinstance(obj['outcome'], str)
```

## Next Steps


---

*Source: test_outcome_hooks.py:576 | Complexity: Intermediate | Last updated: 2026-05-05*