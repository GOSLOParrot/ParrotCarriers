# How To: Run No Retrain When Dry Run

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: dry_run=True is a hard gate: neither path fires.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `datetime`
- `pathlib`
- `pytest`
- `lightgbm`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `numpy`
- `numpy`

**Setup Required:**
```python
# Fixtures: learning_db, memory_db, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'dry_run=True is a hard gate: neither path fires.'

```python
'dry_run=True is a hard gate: neither path fires.'
```

**Verification:**
```python
assert calls['shadow'] == 0
```

### Step 2: Call _seed_active_model()

```python
_seed_active_model(learning_db, profile_id='p', last_retrain_at=datetime.now(timezone.utc) - timedelta(hours=1), new_outcomes=60)
```

**Verification:**
```python
assert calls['legacy'] == 0
```

### Step 3: Call _seed_learning_feedback()

```python
_seed_learning_feedback(learning_db, profile_id='p', n=300)
```

### Step 4: Assign calls = value

```python
calls = {'shadow': 0, 'legacy': 0}
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cw_mod, '_run_shadow_cycle', _fake_shadow)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cw_mod.ConsolidationWorker, '_retrain_ranker', _fake_legacy)
```

### Step 7: Assign worker = cw_mod.ConsolidationWorker(...)

```python
worker = cw_mod.ConsolidationWorker(memory_db=str(memory_db), learning_db=str(learning_db))
```

### Step 8: Call worker.run()

```python
worker.run(profile_id='p', dry_run=True)
```

**Verification:**
```python
assert calls['shadow'] == 0
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, memory_db, monkeypatch

# Workflow
'dry_run=True is a hard gate: neither path fires.'
from superlocalmemory.learning import consolidation_worker as cw_mod
_seed_active_model(learning_db, profile_id='p', last_retrain_at=datetime.now(timezone.utc) - timedelta(hours=1), new_outcomes=60)
_seed_learning_feedback(learning_db, profile_id='p', n=300)
calls = {'shadow': 0, 'legacy': 0}

def _fake_shadow(**kw):
    calls['shadow'] += 1
    return {}

def _fake_legacy(self, pid, sc):
    calls['legacy'] += 1
    return True
monkeypatch.setattr(cw_mod, '_run_shadow_cycle', _fake_shadow)
monkeypatch.setattr(cw_mod.ConsolidationWorker, '_retrain_ranker', _fake_legacy)
worker = cw_mod.ConsolidationWorker(memory_db=str(memory_db), learning_db=str(learning_db))
worker.run(profile_id='p', dry_run=True)
assert calls['shadow'] == 0
assert calls['legacy'] == 0
```

## Next Steps


---

*Source: test_consolidation_online_retrain_wiring.py:343 | Complexity: Advanced | Last updated: 2026-05-05*