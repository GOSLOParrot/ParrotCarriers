# How To: Stop Hook Finalizes All Pending For Session

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: All pending outcomes for the session get finalized into action_outcomes.

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

### Step 1: 'All pending outcomes for the session get finalized into action_outcomes.'

```python
'All pending outcomes for the session get finalized into action_outcomes.'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-A', session_id='sess-F', fact_ids=['f1'])
```

**Verification:**
```python
assert out == '{}'
```

### Step 3: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-B', session_id='sess-F', fact_ids=['f2'])
```

**Verification:**
```python
assert _fetch_action(memory_db, 'oid-A') is not None
```

### Step 4: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-OTHER', session_id='sess-OTHER', fact_ids=['f3'])
```

**Verification:**
```python
assert _fetch_action(memory_db, 'oid-B') is not None
```

### Step 5: Assign payload = value

```python
payload = {'session_id': 'sess-F'}
```

**Verification:**
```python
assert _fetch_action(memory_db, 'oid-OTHER') is None
```

### Step 6: Assign unknown = _invoke_hook(...)

```python
rc, out = _invoke_hook(h.main, payload, monkeypatch)
```

**Verification:**
```python
assert a['status'] == 'settled'
```

### Step 7: Assign a = _fetch_pending(...)

```python
a = _fetch_pending(memory_db, 'oid-A')
```

**Verification:**
```python
assert b['status'] == 'settled'
```

### Step 8: Assign b = _fetch_pending(...)

```python
b = _fetch_pending(memory_db, 'oid-B')
```

**Verification:**
```python
assert a['status'] == 'settled'
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, slm_home, install_token, monkeypatch

# Workflow
'All pending outcomes for the session get finalized into action_outcomes.'
from superlocalmemory.hooks import stop_outcome_hook as h
_seed_pending(memory_db, outcome_id='oid-A', session_id='sess-F', fact_ids=['f1'])
_seed_pending(memory_db, outcome_id='oid-B', session_id='sess-F', fact_ids=['f2'])
_seed_pending(memory_db, outcome_id='oid-OTHER', session_id='sess-OTHER', fact_ids=['f3'])
payload = {'session_id': 'sess-F'}
rc, out = _invoke_hook(h.main, payload, monkeypatch)
assert rc == 0
assert out == '{}'
assert _fetch_action(memory_db, 'oid-A') is not None
assert _fetch_action(memory_db, 'oid-B') is not None
assert _fetch_action(memory_db, 'oid-OTHER') is None
a = _fetch_pending(memory_db, 'oid-A')
b = _fetch_pending(memory_db, 'oid-B')
assert a['status'] == 'settled'
assert b['status'] == 'settled'
```

## Next Steps


---

*Source: test_outcome_hooks.py:441 | Complexity: Advanced | Last updated: 2026-05-05*