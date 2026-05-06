# How To: Phase3 Requires Active And Verified Model

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test phase3 requires active and verified model

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.signals`
- `superlocalmemory.server.routes.learning`
- `tests.test_learning._signal_fixtures`
- `lightgbm`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(tmp_path)
```

**Verification:**
```python
assert _retrain_ranker_impl(db._db_path, 'p1')
```

### Step 2: Call _seed_signals()

```python
_seed_signals(db, n_queries=40, per_query=10)
```

**Verification:**
```python
assert phase['phase'] == 3
```

### Step 3: Assign phase = _compute_ranker_phase(...)

```python
phase = _compute_ranker_phase('p1', learning_db_path=Path(db._db_path))
```

**Verification:**
```python
assert phase['model_active'] is True
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(db._db_path)
```

**Verification:**
```python
assert phase['signals'] == 400
```

### Step 5: Call conn.execute()

```python
conn.execute('UPDATE learning_model_state SET state_bytes = ? WHERE is_active = 1', (b'tampered',))
```

**Verification:**
```python
assert phase2['phase'] == 2
```

### Step 6: Call conn.commit()

```python
conn.commit()
```

**Verification:**
```python
assert phase2['model_active'] is False
```

### Step 7: Call conn.close()

```python
conn.close()
```

### Step 8: Call model_cache.invalidate()

```python
model_cache.invalidate('p1')
```

### Step 9: Assign phase2 = _compute_ranker_phase(...)

```python
phase2 = _compute_ranker_phase('p1', learning_db_path=Path(db._db_path))
```

**Verification:**
```python
assert phase2['phase'] == 2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
_seed_signals(db, n_queries=40, per_query=10)
assert _retrain_ranker_impl(db._db_path, 'p1')
phase = _compute_ranker_phase('p1', learning_db_path=Path(db._db_path))
assert phase['phase'] == 3
assert phase['model_active'] is True
assert phase['signals'] == 400
conn = sqlite3.connect(db._db_path)
conn.execute('UPDATE learning_model_state SET state_bytes = ? WHERE is_active = 1', (b'tampered',))
conn.commit()
conn.close()
model_cache.invalidate('p1')
phase2 = _compute_ranker_phase('p1', learning_db_path=Path(db._db_path))
assert phase2['phase'] == 2
assert phase2['model_active'] is False
```

## Next Steps


---

*Source: test_dashboard_phase_truth.py:66 | Complexity: Advanced | Last updated: 2026-05-05*