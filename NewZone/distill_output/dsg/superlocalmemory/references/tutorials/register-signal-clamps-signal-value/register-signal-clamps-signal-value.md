# How To: Register Signal Clamps Signal Value

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test register signal clamps signal value

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `os`
- `sqlite3`
- `statistics`
- `threading`
- `time`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`

**Setup Required:**
```python
# Fixtures: model, memory_db
```

## Step-by-Step Guide

### Step 1: Assign outcome_id = model.record_recall(...)

```python
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
```

**Verification:**
```python
assert ok is True
```

### Step 2: Assign ok = model.register_signal(...)

```python
ok = model.register_signal(outcome_id=outcome_id, signal_name='dwell_ms', signal_value=99999999)
```

**Verification:**
```python
assert 0 <= stored['dwell_ms'] <= 3600000
```

### Step 3: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, outcome_id)
```

**Verification:**
```python
assert stored['dwell_ms'] == 0
```

### Step 4: Assign stored = json.loads(...)

```python
stored = json.loads(row['signals_json'])
```

**Verification:**
```python
assert 0 <= stored['dwell_ms'] <= 3600000
```

### Step 5: Call model.register_signal()

```python
model.register_signal(outcome_id=outcome_id, signal_name='dwell_ms', signal_value=-500)
```

### Step 6: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, outcome_id)
```

### Step 7: Assign stored = json.loads(...)

```python
stored = json.loads(row['signals_json'])
```

**Verification:**
```python
assert stored['dwell_ms'] == 0
```


## Complete Example

```python
# Setup
# Fixtures: model, memory_db

# Workflow
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
ok = model.register_signal(outcome_id=outcome_id, signal_name='dwell_ms', signal_value=99999999)
assert ok is True
row = _fetch_pending(memory_db, outcome_id)
stored = json.loads(row['signals_json'])
assert 0 <= stored['dwell_ms'] <= 3600000
model.register_signal(outcome_id=outcome_id, signal_name='dwell_ms', signal_value=-500)
row = _fetch_pending(memory_db, outcome_id)
stored = json.loads(row['signals_json'])
assert stored['dwell_ms'] == 0
```

## Next Steps


---

*Source: test_engagement_reward_model.py:258 | Complexity: Intermediate | Last updated: 2026-05-05*