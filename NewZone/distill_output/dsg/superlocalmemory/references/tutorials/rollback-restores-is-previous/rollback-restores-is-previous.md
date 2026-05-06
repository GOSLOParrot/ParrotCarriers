# How To: Rollback Restores Is Previous

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Executing rollback flips current active → is_rollback and
the is_previous row → is_active=1.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `sqlite3`
- `time`
- `uuid`
- `datetime`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.model_rollback`
- `logging`
- `superlocalmemory.learning.model_rollback`
- `numpy`
- `numpy`

**Setup Required:**
```python
# Fixtures: learning_db
```

## Step-by-Step Guide

### Step 1: 'Executing rollback flips current active → is_rollback and\n    the is_previous row → is_active=1.'

```python
'Executing rollback flips current active → is_rollback and\n    the is_previous row → is_active=1.'
```

**Verification:**
```python
assert bad[0] == 0
```

### Step 2: Call _seed_previous_model()

```python
_seed_previous_model(learning_db, profile_id='p', state_bytes=b'old-good')
```

**Verification:**
```python
assert bad[1] == 1
```

### Step 3: Assign active_id = _seed_active_model(...)

```python
active_id = _seed_active_model(learning_db, profile_id='p', new_outcomes=0, state_bytes=b'bad-new')
```

**Verification:**
```python
assert bad[2] == 'test_regression'
```

### Step 4: Assign rb = ModelRollback(...)

```python
rb = ModelRollback(learning_db_path=str(learning_db), profile_id='p', baseline_ndcg=0.5)
```

**Verification:**
```python
assert active is not None
```

### Step 5: Call rb.execute_rollback()

```python
rb.execute_rollback(reason='test_regression')
```

**Verification:**
```python
assert bytes(active[0]) == b'old-good'
```

### Step 6: Assign bad = conn.execute.fetchone(...)

```python
bad = conn.execute('SELECT is_active, is_rollback, rollback_reason FROM learning_model_state WHERE id=?', (active_id,)).fetchone()
```

**Verification:**
```python
assert bad[0] == 0
```

### Step 7: Assign active = conn.execute.fetchone(...)

```python
active = conn.execute("SELECT state_bytes FROM learning_model_state WHERE profile_id='p' AND is_active=1").fetchone()
```

**Verification:**
```python
assert active is not None
```


## Complete Example

```python
# Setup
# Fixtures: learning_db

# Workflow
'Executing rollback flips current active → is_rollback and\n    the is_previous row → is_active=1.'
from superlocalmemory.learning.model_rollback import ModelRollback
_seed_previous_model(learning_db, profile_id='p', state_bytes=b'old-good')
active_id = _seed_active_model(learning_db, profile_id='p', new_outcomes=0, state_bytes=b'bad-new')
rb = ModelRollback(learning_db_path=str(learning_db), profile_id='p', baseline_ndcg=0.5)
rb.execute_rollback(reason='test_regression')
with sqlite3.connect(learning_db) as conn:
    bad = conn.execute('SELECT is_active, is_rollback, rollback_reason FROM learning_model_state WHERE id=?', (active_id,)).fetchone()
    assert bad[0] == 0
    assert bad[1] == 1
    assert bad[2] == 'test_regression'
    active = conn.execute("SELECT state_bytes FROM learning_model_state WHERE profile_id='p' AND is_active=1").fetchone()
    assert active is not None
    assert bytes(active[0]) == b'old-good'
```

## Next Steps


---

*Source: test_online_retrain.py:682 | Complexity: Intermediate | Last updated: 2026-05-05*