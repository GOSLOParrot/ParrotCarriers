# How To: Search Returns Results

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test search returns results

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
assert len(results) == 2
```

### Step 2: Assign cfg = VectorStoreConfig(...)

```python
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
```

**Verification:**
```python
assert results[0][0] == 'f1'
```

### Step 3: Assign vs = VectorStore(...)

```python
vs = VectorStore(db_path, cfg)
```

**Verification:**
```python
assert results[0][1] > results[1][1]
```

### Step 4: Call vs.upsert()

```python
vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
```

### Step 5: Call vs.upsert()

```python
vs.upsert('f2', 'p1', _vec(0, 1, 0, 0))
```

### Step 6: Assign results = vs.search(...)

```python
results = vs.search(_vec(1, 0, 0, 0), top_k=5, profile_id='p1')
```

**Verification:**
```python
assert len(results) == 2
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
vs.upsert('f2', 'p1', _vec(0, 1, 0, 0))
results = vs.search(_vec(1, 0, 0, 0), top_k=5, profile_id='p1')
assert len(results) == 2
assert results[0][0] == 'f1'
assert results[0][1] > results[1][1]
```

## Next Steps


---

*Source: test_vector_store.py:193 | Complexity: Intermediate | Last updated: 2026-05-05*