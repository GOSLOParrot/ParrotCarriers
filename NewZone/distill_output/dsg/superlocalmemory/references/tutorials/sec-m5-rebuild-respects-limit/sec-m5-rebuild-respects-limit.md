# How To: Sec M5 Rebuild Respects Limit

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test sec m5 rebuild respects limit

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`
- `contextlib`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign memory_db = value

```python
memory_db = tmp_path / 'memory.db'
```

**Verification:**
```python
assert n == 1, 'entity_trigrams table must exist after bootstrap'
```

### Step 2: Call _bootstrap_memory_db()

```python
_bootstrap_memory_db(memory_db)
```

### Step 3: Assign cache_db = value

```python
cache_db = tmp_path / 'active_brain_cache.db'
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ti.TrigramIndex, 'CACHE_DB_PATH', cache_db)
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ti, 'ram_reservation', _noop)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ti.TrigramIndex, '_MAX_REBUILD_ROWS', 5, raising=True)
```

### Step 7: Assign idx = ti.TrigramIndex(...)

```python
idx = ti.TrigramIndex(memory_db)
```

### Step 8: Call idx.bootstrap()

```python
idx.bootstrap()
```

**Verification:**
```python
assert n == 1, 'entity_trigrams table must exist after bootstrap'
```

### Step 9: yield

```python
yield
```

### Step 10: Assign unknown = conn.execute.fetchone(...)

```python
n, = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='entity_trigrams'").fetchone()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
memory_db = tmp_path / 'memory.db'
_bootstrap_memory_db(memory_db)
cache_db = tmp_path / 'active_brain_cache.db'
monkeypatch.setattr(ti.TrigramIndex, 'CACHE_DB_PATH', cache_db)
from contextlib import contextmanager

@contextmanager
def _noop(*a, **kw):
    yield
monkeypatch.setattr(ti, 'ram_reservation', _noop)
monkeypatch.setattr(ti.TrigramIndex, '_MAX_REBUILD_ROWS', 5, raising=True)
idx = ti.TrigramIndex(memory_db)
idx.bootstrap()
with sqlite3.connect(cache_db) as conn:
    n, = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='entity_trigrams'").fetchone()
assert n == 1, 'entity_trigrams table must exist after bootstrap'
```

## Next Steps


---

*Source: test_stage8_trigram_rebuild_bound.py:52 | Complexity: Advanced | Last updated: 2026-05-05*