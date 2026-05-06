# How To: Rollback Reason Logged

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: execute_rollback writes rollback_reason on the rollback row AND
logs a warning line carrying profile_id + reason.

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
# Fixtures: learning_db, caplog
```

## Step-by-Step Guide

### Step 1: 'execute_rollback writes rollback_reason on the rollback row AND\n    logs a warning line carrying profile_id + reason.'

```python
'execute_rollback writes rollback_reason on the rollback row AND\n    logs a warning line carrying profile_id + reason.'
```

**Verification:**
```python
assert records, 'rollback log line missing'
```

### Step 2: Call _seed_previous_model()

```python
_seed_previous_model(learning_db, profile_id='p')
```

**Verification:**
```python
assert 'p' in msg
```

### Step 3: Call _seed_active_model()

```python
_seed_active_model(learning_db, profile_id='p')
```

**Verification:**
```python
assert 'bench_regression_v1' in msg
```

### Step 4: Assign rb = ModelRollback(...)

```python
rb = ModelRollback(learning_db_path=str(learning_db), profile_id='p', baseline_ndcg=0.5)
```

**Verification:**
```python
assert reason == 'bench_regression_v1'
```

### Step 5: Call caplog.set_level()

```python
caplog.set_level(logging.WARNING, logger='superlocalmemory.learning.model_rollback')
```

### Step 6: Call rb.execute_rollback()

```python
rb.execute_rollback(reason='bench_regression_v1')
```

### Step 7: Assign records = value

```python
records = [r for r in caplog.records if 'rollback' in r.getMessage().lower()]
```

**Verification:**
```python
assert records, 'rollback log line missing'
```

### Step 8: Assign msg = unknown.getMessage(...)

```python
msg = records[-1].getMessage()
```

**Verification:**
```python
assert 'p' in msg
```

### Step 9: Assign reason = value

```python
reason = conn.execute("SELECT rollback_reason FROM learning_model_state WHERE profile_id='p' AND is_rollback=1").fetchone()[0]
```

**Verification:**
```python
assert reason == 'bench_regression_v1'
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, caplog

# Workflow
'execute_rollback writes rollback_reason on the rollback row AND\n    logs a warning line carrying profile_id + reason.'
import logging
from superlocalmemory.learning.model_rollback import ModelRollback
_seed_previous_model(learning_db, profile_id='p')
_seed_active_model(learning_db, profile_id='p')
rb = ModelRollback(learning_db_path=str(learning_db), profile_id='p', baseline_ndcg=0.5)
caplog.set_level(logging.WARNING, logger='superlocalmemory.learning.model_rollback')
rb.execute_rollback(reason='bench_regression_v1')
records = [r for r in caplog.records if 'rollback' in r.getMessage().lower()]
assert records, 'rollback log line missing'
msg = records[-1].getMessage()
assert 'p' in msg
assert 'bench_regression_v1' in msg
with sqlite3.connect(learning_db) as conn:
    reason = conn.execute("SELECT rollback_reason FROM learning_model_state WHERE profile_id='p' AND is_rollback=1").fetchone()[0]
    assert reason == 'bench_regression_v1'
```

## Next Steps


---

*Source: test_online_retrain.py:758 | Complexity: Advanced | Last updated: 2026-05-05*