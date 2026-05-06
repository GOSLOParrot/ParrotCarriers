# How To: Search Similarity Scores Valid

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test search similarity scores valid

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
assert len(results) == 1
```

### Step 2: Assign cfg = VectorStoreConfig(...)

```python
cfg = VectorStoreConfig(dimension=DIM, enabled=True)
```

**Verification:**
```python
assert fid == 'f1'
```

### Step 3: Assign vs = VectorStore(...)

```python
vs = VectorStore(db_path, cfg)
```

**Verification:**
```python
assert 0.0 <= score <= 1.0
```

### Step 4: Call vs.upsert()

```python
vs.upsert('f1', 'p1', _vec(1, 0, 0, 0))
```

**Verification:**
```python
assert score > 0.9
```

### Step 5: Assign results = vs.search(...)

```python
results = vs.search(_vec(1, 0, 0, 0), top_k=1, profile_id='p1')
```

**Verification:**
```python
assert len(results) == 1
```

### Step 6: Assign unknown = value

```python
fid, score = results[0]
```

**Verification:**
```python
assert fid == 'f1'
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
results = vs.search(_vec(1, 0, 0, 0), top_k=1, profile_id='p1')
assert len(results) == 1
fid, score = results[0]
assert fid == 'f1'
assert 0.0 <= score <= 1.0
assert score > 0.9
```

## Next Steps


---

*Source: test_vector_store.py:243 | Complexity: Intermediate | Last updated: 2026-05-05*