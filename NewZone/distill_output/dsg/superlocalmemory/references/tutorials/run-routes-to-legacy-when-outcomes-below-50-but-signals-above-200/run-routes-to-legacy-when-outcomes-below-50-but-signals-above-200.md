# How To: Run Routes To Legacy When Outcomes Below 50 But Signals Above 200

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Legacy cold-start path remains reachable for profiles whose
active model has not yet accumulated 50 outcomes.

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

### Step 1: 'Legacy cold-start path remains reachable for profiles whose\n    active model has not yet accumulated 50 outcomes.'

```python
'Legacy cold-start path remains reachable for profiles whose\n    active model has not yet accumulated 50 outcomes.'
```

**Verification:**
```python
assert shadow_called['flag'] is False
```

### Step 2: Call _seed_learning_feedback()

```python
_seed_learning_feedback(learning_db, profile_id='p', n=250)
```

**Verification:**
```python
assert legacy_called['flag'] is True
```

### Step 3: Assign shadow_called = value

```python
shadow_called = {'flag': False}
```

**Verification:**
```python
assert stats.get('retrained') is True
```

### Step 4: Assign legacy_called = value

```python
legacy_called = {'flag': False}
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cw_mod, '_run_shadow_cycle', _fake_shadow_cycle)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cw_mod.ConsolidationWorker, '_retrain_ranker', _fake_legacy)
```

### Step 7: Assign worker = cw_mod.ConsolidationWorker(...)

```python
worker = cw_mod.ConsolidationWorker(memory_db=str(memory_db), learning_db=str(learning_db))
```

### Step 8: Assign stats = worker.run(...)

```python
stats = worker.run(profile_id='p', dry_run=False)
```

**Verification:**
```python
assert shadow_called['flag'] is False
```

### Step 9: Assign unknown = True

```python
shadow_called['flag'] = True
```

### Step 10: Assign unknown = True

```python
legacy_called['flag'] = True
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, memory_db, monkeypatch

# Workflow
'Legacy cold-start path remains reachable for profiles whose\n    active model has not yet accumulated 50 outcomes.'
from superlocalmemory.learning import consolidation_worker as cw_mod
_seed_learning_feedback(learning_db, profile_id='p', n=250)
shadow_called = {'flag': False}
legacy_called = {'flag': False}

def _fake_shadow_cycle(**kw):
    shadow_called['flag'] = True
    return {}

def _fake_legacy(self, pid, sc):
    legacy_called['flag'] = True
    return True
monkeypatch.setattr(cw_mod, '_run_shadow_cycle', _fake_shadow_cycle)
monkeypatch.setattr(cw_mod.ConsolidationWorker, '_retrain_ranker', _fake_legacy)
worker = cw_mod.ConsolidationWorker(memory_db=str(memory_db), learning_db=str(learning_db))
stats = worker.run(profile_id='p', dry_run=False)
assert shadow_called['flag'] is False
assert legacy_called['flag'] is True
assert stats.get('retrained') is True
```

## Next Steps


---

*Source: test_consolidation_online_retrain_wiring.py:309 | Complexity: Advanced | Last updated: 2026-05-05*