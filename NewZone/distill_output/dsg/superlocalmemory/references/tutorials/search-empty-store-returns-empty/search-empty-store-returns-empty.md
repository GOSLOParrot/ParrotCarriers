# How To: Search Empty Store Returns Empty

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test search empty store returns empty

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
assert results == []
```

### Step 2: Assign cfg = VectorStoreConfig(...)

```python
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
```

### Step 3: Assign vs = VectorStore(...)

```python
vs = VectorStore(db_path, cfg)
```

### Step 4: Assign results = vs.search(...)

```python
results = vs.search(_vec(1, 0, 0, 0), top_k=5, profile_id='p1')
```

**Verification:**
```python
assert results == []
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db_path = _make_db(tmp_path)
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
vs = VectorStore(db_path, cfg)
results = vs.search(_vec(1, 0, 0, 0), top_k=5, profile_id='p1')
assert results == []
```

## Next Steps


---

*Source: test_vector_store.py:226 | Complexity: Intermediate | Last updated: 2026-05-05*