# How To: User Prompt Rehash Writes Requery On Dup Topic

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Same topic signature within 60 s + prior outcome → requery signal.

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

### Step 1: 'Same topic signature within 60 s + prior outcome → requery signal.'

```python
'Same topic signature within 60 s + prior outcome → requery signal.'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Call _seed_pending()

```python
_seed_pending(memory_db, outcome_id='oid-rehash-1', session_id='sess-R', fact_ids=['fx'])
```

**Verification:**
```python
assert out == '{}'
```

### Step 3: Assign prompt = 'How do I close the recall-outcome loop in SLM?'

```python
prompt = 'How do I close the recall-outcome loop in SLM?'
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
assert signals.get('requery') is True
```

### Step 5: Assign ss_dir = value

```python
ss_dir = slm_home / 'session_state'
```

### Step 6: Call ss_dir.mkdir()

```python
ss_dir.mkdir(parents=True, exist_ok=True)
```

### Step 7: Assign state = value

```python
state = {'last_topic_sig': sig, 'last_prompt_ts_ms': int(time.time() * 1000), 'last_outcome_id': 'oid-rehash-1'}
```

### Step 8: Call unknown.write_text()

```python
(ss_dir / 'sess-R.json').write_text(json.dumps(state))
```

### Step 9: Assign payload = value

```python
payload = {'session_id': 'sess-R', 'prompt': prompt}
```

### Step 10: Assign unknown = _invoke_hook(...)

```python
rc, out = _invoke_hook(h.main, payload, monkeypatch)
```

**Verification:**
```python
assert rc == 0
```

### Step 11: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, 'oid-rehash-1')
```

**Verification:**
```python
assert row is not None
```

### Step 12: Assign signals = json.loads(...)

```python
signals = json.loads(row['signals_json'])
```

**Verification:**
```python
assert signals.get('requery') is True
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, slm_home, install_token, monkeypatch

# Workflow
'Same topic signature within 60 s + prior outcome → requery signal.'
from superlocalmemory.hooks import user_prompt_rehash_hook as h
_seed_pending(memory_db, outcome_id='oid-rehash-1', session_id='sess-R', fact_ids=['fx'])
from superlocalmemory.core.topic_signature import compute_topic_signature
prompt = 'How do I close the recall-outcome loop in SLM?'
sig = compute_topic_signature(prompt)
ss_dir = slm_home / 'session_state'
ss_dir.mkdir(parents=True, exist_ok=True)
state = {'last_topic_sig': sig, 'last_prompt_ts_ms': int(time.time() * 1000), 'last_outcome_id': 'oid-rehash-1'}
(ss_dir / 'sess-R.json').write_text(json.dumps(state))
payload = {'session_id': 'sess-R', 'prompt': prompt}
rc, out = _invoke_hook(h.main, payload, monkeypatch)
assert rc == 0
assert out == '{}'
row = _fetch_pending(memory_db, 'oid-rehash-1')
assert row is not None
signals = json.loads(row['signals_json'])
assert signals.get('requery') is True
```

## Next Steps


---

*Source: test_outcome_hooks.py:360 | Complexity: Advanced | Last updated: 2026-05-05*