# How To: Load Active Handles Bad Feature Names Json

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test load active handles bad feature names json

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pytest`
- `lightgbm`
- `numpy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.labeler`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.ranker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `lightgbm`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `json`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign sub = value

```python
sub = tmp_path / 'corrupt'
```

**Verification:**
```python
assert m is not None
```

### Step 2: Call sub.mkdir()

```python
sub.mkdir()
```

### Step 3: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(sub)
```

### Step 4: Assign conn2 = open_conn(...)

```python
conn2 = open_conn(db)
```

### Step 5: Call conn2.close()

```python
conn2.close()
```

### Step 6: Call _retrain_ranker_impl()

```python
_retrain_ranker_impl(db._db_path, 'p1')
```

### Step 7: Assign direct = sqlite3.connect(...)

```python
direct = sqlite3.connect(db._db_path)
```

### Step 8: Call direct.execute()

```python
direct.execute('UPDATE learning_model_state SET feature_names = ? WHERE is_active=1', ('this is not JSON',))
```

### Step 9: Call direct.commit()

```python
direct.commit()
```

### Step 10: Call direct.close()

```python
direct.close()
```

### Step 11: Call model_cache.invalidate()

```python
model_cache.invalidate('p1')
```

### Step 12: Assign m = load_active(...)

```python
m = load_active(db, 'p1', use_cache=False)
```

**Verification:**
```python
assert m is not None
```

### Step 13: Call record_signal_batch()

```python
record_signal_batch(conn2, make_batch(query_id=f'q{q}', n_candidates=10))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
sub = tmp_path / 'corrupt'
sub.mkdir()
db = make_db_with_migrations(sub)
conn2 = open_conn(db)
for q in range(20):
    record_signal_batch(conn2, make_batch(query_id=f'q{q}', n_candidates=10))
conn2.close()
_retrain_ranker_impl(db._db_path, 'p1')
direct = sqlite3.connect(db._db_path)
direct.execute('UPDATE learning_model_state SET feature_names = ? WHERE is_active=1', ('this is not JSON',))
direct.commit()
direct.close()
model_cache.invalidate('p1')
m = load_active(db, 'p1', use_cache=False)
assert m is not None
```

## Next Steps


---

*Source: test_ranker_v2.py:166 | Complexity: Advanced | Last updated: 2026-05-05*