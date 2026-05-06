# How To: Shadow Gate Keeps Old When Not Better

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test shadow test gate keeps old when not better

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
assert _retrain_ranker_impl(db._db_path, 'p1')
```

### Step 2: Call _seed_training_rows()

```python
_seed_training_rows(db)
```

**Verification:**
```python
assert row_a is not None
```

### Step 3: Assign row_a = db.load_active_model(...)

```python
row_a = db.load_active_model('p1')
```

**Verification:**
```python
assert row_b is not None
```

### Step 4: Assign sha_a = value

```python
sha_a = row_a['bytes_sha256']
```

**Verification:**
```python
assert hashlib.sha256(row_b['state_bytes']).hexdigest() == row_b['bytes_sha256']
```

### Step 5: Call _retrain_ranker_impl()

```python
_retrain_ranker_impl(db._db_path, 'p1')
```

**Verification:**
```python
assert row_b['bytes_sha256'] == sha_a
```

### Step 6: Assign row_b = db.load_active_model(...)

```python
row_b = db.load_active_model('p1')
```

**Verification:**
```python
assert row_b is not None
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
_seed_training_rows(db)
assert _retrain_ranker_impl(db._db_path, 'p1')
row_a = db.load_active_model('p1')
assert row_a is not None
sha_a = row_a['bytes_sha256']
_retrain_ranker_impl(db._db_path, 'p1')
row_b = db.load_active_model('p1')
assert row_b is not None
assert hashlib.sha256(row_b['state_bytes']).hexdigest() == row_b['bytes_sha256']
assert row_b['bytes_sha256'] == sha_a
```

## Next Steps


---

*Source: test_lightgbm_training.py:224 | Complexity: Intermediate | Last updated: 2026-05-05*