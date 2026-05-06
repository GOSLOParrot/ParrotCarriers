# How To: Model Roundtrip Via Model To String

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test model roundtrip via model to string

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
assert model is not None
```

### Step 3: Assign model = load_active(...)

```python
model = load_active(db, 'p1', use_cache=False)
```

**Verification:**
```python
assert preds.shape == (3,)
```

### Step 4: Assign X = np.zeros(...)

```python
X = np.zeros((3, len(FEATURE_NAMES)), dtype=np.float32)
```

### Step 5: Assign preds = model.booster.predict(...)

```python
preds = model.booster.predict(X)
```

**Verification:**
```python
assert preds.shape == (3,)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
_seed_training_rows(db)
assert _retrain_ranker_impl(db._db_path, 'p1')
model = load_active(db, 'p1', use_cache=False)
assert model is not None
X = np.zeros((3, len(FEATURE_NAMES)), dtype=np.float32)
preds = model.booster.predict(X)
assert preds.shape == (3,)
```

## Next Steps


---

*Source: test_lightgbm_training.py:112 | Complexity: Intermediate | Last updated: 2026-05-05*