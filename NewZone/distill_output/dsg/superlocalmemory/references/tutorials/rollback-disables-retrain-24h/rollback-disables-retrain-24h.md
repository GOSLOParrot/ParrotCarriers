# How To: Rollback Disables Retrain 24H

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: After rollback, metadata_json.retrain_disabled_until is set
≥24h in the future; ``_should_retrain`` returns False until then.

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

### Step 1: 'After rollback, metadata_json.retrain_disabled_until is set\n    ≥24h in the future; ``_should_retrain`` returns False until then.'

```python
'After rollback, metadata_json.retrain_disabled_until is set\n    ≥24h in the future; ``_should_retrain`` returns False until then.'
```

**Verification:**
```python
assert disabled_until is not None
```

### Step 2: Call _seed_previous_model()

```python
_seed_previous_model(learning_db, profile_id='p')
```

**Verification:**
```python
assert delta_h >= 23.5
```

### Step 3: Call _seed_active_model()

```python
_seed_active_model(learning_db, profile_id='p', new_outcomes=500)
```

**Verification:**
```python
assert worker._should_retrain(profile_id='p') is False
```

### Step 4: Assign rb = ModelRollback(...)

```python
rb = ModelRollback(learning_db_path=str(learning_db), profile_id='p', baseline_ndcg=0.5)
```

### Step 5: Call rb.execute_rollback()

```python
rb.execute_rollback(reason='regression')
```

### Step 6: Assign worker = ConsolidationWorker(...)

```python
worker = ConsolidationWorker(memory_db=':memory:', learning_db=str(learning_db))
```

**Verification:**
```python
assert worker._should_retrain(profile_id='p') is False
```

### Step 7: Assign meta_raw = value

```python
meta_raw = conn.execute("SELECT metadata_json FROM learning_model_state WHERE profile_id='p' AND is_active=1").fetchone()[0]
```

### Step 8: Assign meta = json.loads(...)

```python
meta = json.loads(meta_raw or '{}')
```

### Step 9: Assign disabled_until = meta.get(...)

```python
disabled_until = meta.get('retrain_disabled_until')
```

**Verification:**
```python
assert disabled_until is not None
```

### Step 10: Assign parsed = datetime.fromisoformat(...)

```python
parsed = datetime.fromisoformat(disabled_until)
```

### Step 11: Assign now = datetime.now(...)

```python
now = datetime.now(timezone.utc)
```

### Step 12: Assign delta_h = value

```python
delta_h = (parsed - now).total_seconds() / 3600.0
```

**Verification:**
```python
assert delta_h >= 23.5
```

### Step 13: Assign parsed = parsed.replace(...)

```python
parsed = parsed.replace(tzinfo=timezone.utc)
```


## Complete Example

```python
# Setup
# Fixtures: learning_db

# Workflow
'After rollback, metadata_json.retrain_disabled_until is set\n    ≥24h in the future; ``_should_retrain`` returns False until then.'
from superlocalmemory.learning.consolidation_worker import ConsolidationWorker
from superlocalmemory.learning.model_rollback import ModelRollback
_seed_previous_model(learning_db, profile_id='p')
_seed_active_model(learning_db, profile_id='p', new_outcomes=500)
rb = ModelRollback(learning_db_path=str(learning_db), profile_id='p', baseline_ndcg=0.5)
rb.execute_rollback(reason='regression')
with sqlite3.connect(learning_db) as conn:
    meta_raw = conn.execute("SELECT metadata_json FROM learning_model_state WHERE profile_id='p' AND is_active=1").fetchone()[0]
    meta = json.loads(meta_raw or '{}')
    disabled_until = meta.get('retrain_disabled_until')
    assert disabled_until is not None
    parsed = datetime.fromisoformat(disabled_until)
    now = datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta_h = (parsed - now).total_seconds() / 3600.0
    assert delta_h >= 23.5
worker = ConsolidationWorker(memory_db=':memory:', learning_db=str(learning_db))
assert worker._should_retrain(profile_id='p') is False
```

## Next Steps


---

*Source: test_online_retrain.py:720 | Complexity: Advanced | Last updated: 2026-05-05*