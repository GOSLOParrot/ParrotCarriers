# How To: User Prompt Rehash Ignores Stale Prior

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Prior prompt >60 s old → no requery signal written.

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

### Step 1: 'Prior prompt >60 s old → no requery signal written.'

```python
'Prior prompt >60 s old → no requery signal written.'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-stale', session_id='sess-S', fact_ids=['fy'])
```

**Verification:**
```python
assert out == '{}'
```

### Step 3: Assign prompt = 'different prompt but matching signature'

```python
prompt = 'different prompt but matching signature'
```

**Verification:**
```python
assert row is not None
```

### Step 4: Assign sig = compute_topic_signature(...)

```python
sig = compute_topic_signature(prompt)
```

**Verification:**
```python
assert 'requery' not in signals
```

### Step 5: Assign ss_dir = value

```python
ss_dir = slm_home / 'session_state'
```

### Step 6: Call ss_dir.mkdir()

```python
ss_dir.mkdir(parents=True, exist_ok=True)
```

### Step 7: Assign stale_ts = value

```python
stale_ts = int(time.time() * 1000) - 5 * 60 * 1000
```

### Step 8: Assign state = value

```python
state = {'last_topic_sig': sig, 'last_prompt_ts_ms': stale_ts, 'last_outcome_id': 'oid-stale'}
```

### Step 9: Call unknown.write_text()

```python
(ss_dir / 'sess-S.json').write_text(json.dumps(state))
```

### Step 10: Assign payload = value

```python
payload = {'session_id': 'sess-S', 'prompt': prompt}
```

### Step 11: Assign unknown = _invoke_hook(...)

```python
rc, out = _invoke_hook(h.main, payload, monkeypatch)
```

**Verification:**
```python
assert rc == 0
```

### Step 12: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, 'oid-stale')
```

**Verification:**
```python
assert row is not None
```

### Step 13: Assign signals = json.loads(...)

```python
signals = json.loads(row['signals_json'])
```

**Verification:**
```python
assert 'requery' not in signals
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, slm_home, install_token, monkeypatch

# Workflow
'Prior prompt >60 s old → no requery signal written.'
from superlocalmemory.hooks import user_prompt_rehash_hook as h
_seed_pending(memory_db, outcome_id='oid-stale', session_id='sess-S', fact_ids=['fy'])
from superlocalmemory.core.topic_signature import compute_topic_signature
prompt = 'different prompt but matching signature'
sig = compute_topic_signature(prompt)
ss_dir = slm_home / 'session_state'
ss_dir.mkdir(parents=True, exist_ok=True)
stale_ts = int(time.time() * 1000) - 5 * 60 * 1000
state = {'last_topic_sig': sig, 'last_prompt_ts_ms': stale_ts, 'last_outcome_id': 'oid-stale'}
(ss_dir / 'sess-S.json').write_text(json.dumps(state))
payload = {'session_id': 'sess-S', 'prompt': prompt}
rc, out = _invoke_hook(h.main, payload, monkeypatch)
assert rc == 0
assert out == '{}'
row = _fetch_pending(memory_db, 'oid-stale')
assert row is not None
signals = json.loads(row['signals_json'])
assert 'requery' not in signals
```

## Next Steps


---

*Source: test_outcome_hooks.py:399 | Complexity: Advanced | Last updated: 2026-05-05*