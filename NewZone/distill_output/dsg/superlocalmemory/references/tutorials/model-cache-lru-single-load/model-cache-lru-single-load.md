# How To: Model Cache Lru Single Load

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test model cache lru single load

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
assert all((r is not None for r in results))
```

### Step 3: Assign counting = _CountingDB(...)

```python
counting = _CountingDB(db)
```

**Verification:**
```python
assert len({id(r) for r in results}) == 1
```

### Step 4: Call model_cache.invalidate()

```python
model_cache.invalidate('p1')
```

**Verification:**
```python
assert counting.calls == 1
```

### Step 5: Assign results = value

```python
results = []
```

### Step 6: Assign threads = value

```python
threads = [threading.Thread(target=worker) for _ in range(10)]
```

**Verification:**
```python
assert all((r is not None for r in results))
```

### Step 7: Call results.append()

```python
results.append(load_active(counting, 'p1'))
```

### Step 8: Call t.start()

```python
t.start()
```

### Step 9: Call t.join()

```python
t.join()
```

### Step 10: Assign self._inner = inner

```python
self._inner = inner
```

### Step 11: Assign self.calls = 0

```python
self.calls = 0
```

### Step 12: Assign self._lock = threading.Lock(...)

```python
self._lock = threading.Lock()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
_seed_training_rows(db)
assert _retrain_ranker_impl(db._db_path, 'p1')

class _CountingDB:

    def __init__(self, inner):
        self._inner = inner
        self.calls = 0
        self._lock = threading.Lock()

    def load_active_model(self, profile_id):
        with self._lock:
            self.calls += 1
        return self._inner.load_active_model(profile_id)
counting = _CountingDB(db)
model_cache.invalidate('p1')
results = []

def worker():
    results.append(load_active(counting, 'p1'))
threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
assert all((r is not None for r in results))
assert len({id(r) for r in results}) == 1
assert counting.calls == 1
```

## Next Steps


---

*Source: test_lightgbm_training.py:252 | Complexity: Advanced | Last updated: 2026-05-05*