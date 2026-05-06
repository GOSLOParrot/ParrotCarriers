# How To: Group Param Required Returns False When Single Query

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test group param required returns false when single query

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `sqlite3`
- `threading`
- `pathlib`
- `pytest`
- `lightgbm`
- `numpy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.database`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.labeler`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.ranker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `lightgbm`
- `re`
- `re`
- `re`
- `re`

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
assert ok is False
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

### Step 3: Call conn.close()

```python
conn.close()
```

### Step 4: Assign ok = _retrain_ranker_impl(...)

```python
ok = _retrain_ranker_impl(db._db_path, 'p1')
```

**Verification:**
```python
assert ok is False
```

### Step 5: Assign batch = make_batch(...)

```python
batch = make_batch(profile_id='p1', query_id='q-single', query_text='solo', n_candidates=10)
```

### Step 6: Call record_signal_batch()

```python
record_signal_batch(conn, batch)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
for i in range(25):
    batch = make_batch(profile_id='p1', query_id='q-single', query_text='solo', n_candidates=10)
    record_signal_batch(conn, batch)
conn.close()
ok = _retrain_ranker_impl(db._db_path, 'p1')
assert ok is False
```

## Next Steps


---

*Source: test_lightgbm_training.py:90 | Complexity: Intermediate | Last updated: 2026-05-05*