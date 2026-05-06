# How To: Post Tool Hook Writes Signal On Hmac Match

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Valid HMAC marker in tool_response → register_signal recorded.

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

### Step 1: 'Valid HMAC marker in tool_response → register_signal recorded.'

```python
'Valid HMAC marker in tool_response → register_signal recorded.'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-ok-1', session_id='sess-A', fact_ids=['fact-42'])
```

**Verification:**
```python
assert out == '{}'
```

### Step 3: Assign marker = _make_marker(...)

```python
marker = _make_marker('fact-42')
```

**Verification:**
```python
assert row is not None
```

### Step 4: Assign payload = value

```python
payload = {'session_id': 'sess-A', 'tool_name': 'Edit', 'tool_response': f'some text {marker} more text'}
```

**Verification:**
```python
assert signals.get('edit') is True
```

### Step 5: Assign unknown = _invoke_hook(...)

```python
rc, out = _invoke_hook(h.main, payload, monkeypatch)
```

**Verification:**
```python
assert rc == 0
```

### Step 6: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, 'oid-ok-1')
```

**Verification:**
```python
assert row is not None
```

### Step 7: Assign signals = json.loads(...)

```python
signals = json.loads(row['signals_json'])
```

**Verification:**
```python
assert signals.get('edit') is True
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, slm_home, install_token, monkeypatch

# Workflow
'Valid HMAC marker in tool_response → register_signal recorded.'
from superlocalmemory.hooks import post_tool_outcome_hook as h
_seed_pending(memory_db, outcome_id='oid-ok-1', session_id='sess-A', fact_ids=['fact-42'])
marker = _make_marker('fact-42')
payload = {'session_id': 'sess-A', 'tool_name': 'Edit', 'tool_response': f'some text {marker} more text'}
rc, out = _invoke_hook(h.main, payload, monkeypatch)
assert rc == 0
assert out == '{}'
row = _fetch_pending(memory_db, 'oid-ok-1')
assert row is not None
signals = json.loads(row['signals_json'])
assert signals.get('edit') is True
```

## Next Steps


---

*Source: test_outcome_hooks.py:181 | Complexity: Intermediate | Last updated: 2026-05-05*