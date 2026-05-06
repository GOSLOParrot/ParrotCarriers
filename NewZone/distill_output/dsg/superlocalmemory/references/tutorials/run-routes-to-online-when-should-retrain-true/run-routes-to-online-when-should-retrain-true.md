# How To: Run Routes To Online When Should Retrain True

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: run() MUST dispatch ``_run_shadow_cycle`` when the trigger is True.

Previously dead — run() only ever hit the legacy path.

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

### Step 1: 'run() MUST dispatch ``_run_shadow_cycle`` when the trigger is True.\n\n    Previously dead — run() only ever hit the legacy path.\n    '

```python
'run() MUST dispatch ``_run_shadow_cycle`` when the trigger is True.\n\n    Previously dead — run() only ever hit the legacy path.\n    '
```

**Verification:**
```python
assert captured.get('called') is True
```

### Step 2: Call _seed_active_model()

```python
_seed_active_model(learning_db, profile_id='p', last_retrain_at=datetime.now(timezone.utc) - timedelta(hours=1), new_outcomes=60)
```

**Verification:**
```python
assert captured.get('legacy_called') is not True
```

### Step 3: Call _seed_learning_feedback()

```python
_seed_learning_feedback(learning_db, profile_id='p', n=300)
```

**Verification:**
```python
assert captured.get('profile_id') == 'p'
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cw_mod, '_run_shadow_cycle', _fake_shadow_cycle)
```

**Verification:**
```python
assert captured.get('learning_db_path') == str(learning_db)
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cw_mod.ConsolidationWorker, '_retrain_ranker', lambda self, pid, sc: _fake_legacy_retrain(pid, sc))
```

**Verification:**
```python
assert stats.get('online_retrain') is not None
```

### Step 6: Assign worker = cw_mod.ConsolidationWorker(...)

```python
worker = cw_mod.ConsolidationWorker(memory_db=str(memory_db), learning_db=str(learning_db))
```

### Step 7: Assign stats = worker.run(...)

```python
stats = worker.run(profile_id='p', dry_run=False)
```

**Verification:**
```python
assert captured.get('called') is True
```

### Step 8: Assign unknown = True

```python
captured['called'] = True
```

### Step 9: Assign unknown = profile_id

```python
captured['profile_id'] = profile_id
```

### Step 10: Assign unknown = memory_db_path

```python
captured['memory_db_path'] = memory_db_path
```

### Step 11: Assign unknown = learning_db_path

```python
captured['learning_db_path'] = learning_db_path
```

### Step 12: Assign unknown = True

```python
captured['legacy_called'] = True
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, memory_db, monkeypatch

# Workflow
'run() MUST dispatch ``_run_shadow_cycle`` when the trigger is True.\n\n    Previously dead — run() only ever hit the legacy path.\n    '
from superlocalmemory.learning import consolidation_worker as cw_mod
_seed_active_model(learning_db, profile_id='p', last_retrain_at=datetime.now(timezone.utc) - timedelta(hours=1), new_outcomes=60)
_seed_learning_feedback(learning_db, profile_id='p', n=300)
captured: dict = {}

def _fake_shadow_cycle(*, memory_db_path, learning_db_path, profile_id):
    captured['called'] = True
    captured['profile_id'] = profile_id
    captured['memory_db_path'] = memory_db_path
    captured['learning_db_path'] = learning_db_path
    return {'aborted': None, 'candidate_persisted': True, 'promoted': False, 'metrics': {'mean_score': 0.5}}

def _fake_legacy_retrain(profile_id, signal_count):
    captured['legacy_called'] = True
    return True
monkeypatch.setattr(cw_mod, '_run_shadow_cycle', _fake_shadow_cycle)
monkeypatch.setattr(cw_mod.ConsolidationWorker, '_retrain_ranker', lambda self, pid, sc: _fake_legacy_retrain(pid, sc))
worker = cw_mod.ConsolidationWorker(memory_db=str(memory_db), learning_db=str(learning_db))
stats = worker.run(profile_id='p', dry_run=False)
assert captured.get('called') is True
assert captured.get('legacy_called') is not True
assert captured.get('profile_id') == 'p'
assert captured.get('learning_db_path') == str(learning_db)
assert stats.get('online_retrain') is not None
```

## Next Steps


---

*Source: test_consolidation_online_retrain_wiring.py:259 | Complexity: Advanced | Last updated: 2026-05-05*