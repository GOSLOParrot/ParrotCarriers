# How To: Search Profile Isolation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test search profile isolation

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
assert len(results_p1) == 1
```

### Step 2: Assign cfg = VectorStoreConfig(...)

```python
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
```

**Verification:**
```python
assert results_p1[0][0] == 'f1'
```

### Step 3: Assign vs = VectorStore(...)

```python
vs = VectorStore(db_path, cfg)
```

### Step 4: Call vs.upsert()

```python
vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
```

### Step 5: Call vs.upsert()

```python
vs.upsert('f2', 'p2', _vec(0, 1, 0, 0))
```

### Step 6: Assign results_p1 = vs.search(...)

```python
results_p1 = vs.search(_vec(1, 0, 0, 0), top_k=5, profile_id='p1')
```

**Verification:**
```python
assert len(results_p1) == 1
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
vs.upsert('f2', 'p2', _vec(0, 1, 0, 0))
results_p1 = vs.search(_vec(1, 0, 0, 0), top_k=5, profile_id='p1')
assert len(results_p1) == 1
assert results_p1[0][0] == 'f1'
```

## Next Steps


---

*Source: test_vector_store.py:205 | Complexity: Intermediate | Last updated: 2026-05-05*