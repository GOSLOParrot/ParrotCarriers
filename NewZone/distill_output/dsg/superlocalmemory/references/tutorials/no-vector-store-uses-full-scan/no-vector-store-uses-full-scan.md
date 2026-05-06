# How To: No Vector Store Uses Full Scan

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no vector store uses full scan

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.semantic_channel`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Call _seed_fact()

```python
_seed_fact(db, 'default', 'Alice went to Paris', seed=1)
```

**Verification:**
```python
assert len(results) >= 1
```

### Step 2: Call _seed_fact()

```python
_seed_fact(db, 'default', 'Bob stayed in London', seed=2)
```

**Verification:**
```python
assert len(fact_ids) > 0
```

### Step 3: Assign ch = SemanticChannel(...)

```python
ch = SemanticChannel(db, vector_store=None)
```

### Step 4: Assign query = _make_embedding(...)

```python
query = _make_embedding(1)
```

### Step 5: Assign results = ch.search(...)

```python
results = ch.search(query, 'default', top_k=5)
```

**Verification:**
```python
assert len(results) >= 1
```

### Step 6: Assign fact_ids = value

```python
fact_ids = [fid for fid, _ in results]
```

**Verification:**
```python
assert len(fact_ids) > 0
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
_seed_fact(db, 'default', 'Alice went to Paris', seed=1)
_seed_fact(db, 'default', 'Bob stayed in London', seed=2)
ch = SemanticChannel(db, vector_store=None)
query = _make_embedding(1)
results = ch.search(query, 'default', top_k=5)
assert len(results) >= 1
fact_ids = [fid for fid, _ in results]
assert len(fact_ids) > 0
```

## Next Steps


---

*Source: test_semantic_channel_with_vec.py:75 | Complexity: Intermediate | Last updated: 2026-05-05*