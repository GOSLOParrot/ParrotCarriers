# How To: Delete Existing

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test delete existing

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
assert vs.count() == 1
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
assert vs.count() == 0
```

### Step 4: Call vs.upsert()

```python
vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
```

**Verification:**
```python
assert vs.count() == 1
```

### Step 5: Assign result = vs.delete(...)

```python
result = vs.delete('f1')
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
vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
assert vs.count() == 1
result = vs.delete('f1')
assert result is True
assert vs.count() == 0
```

## Next Steps


---

*Source: test_vector_store.py:260 | Complexity: Intermediate | Last updated: 2026-05-05*