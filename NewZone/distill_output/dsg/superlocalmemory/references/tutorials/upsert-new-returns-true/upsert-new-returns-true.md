# How To: Upsert New Returns True

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test upsert new returns true

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.vector_store`
- `superlocalmemory.storage`
- `sqlite3`
- `sqlite3`
- `sqlite_vec`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db_path = _make_db(...)

```python
db_path = _make_db(tmp_path)
```

**Verification:**
```python
assert vs.available
```

### Step 2: Assign cfg = VectorStoreConfig(...)

```python
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
```

**Verification:**
```python
assert result is True
```

### Step 3: Assign vs = VectorStore(...)

```python
vs = VectorStore(db_path, cfg)
```

**Verification:**
```python
assert vs.available
```

### Step 4: Assign result = vs.upsert(...)

```python
result = vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
```

**Verification:**
```python
assert result is True
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db_path = _make_db(tmp_path)
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
vs = VectorStore(db_path, cfg)
assert vs.available
result = vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
assert result is True
```

## Next Steps


---

*Source: test_vector_store.py:162 | Complexity: Intermediate | Last updated: 2026-05-05*