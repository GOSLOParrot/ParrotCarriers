# How To: Cache Hit Returns Cached Results

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Second search on same profile with same count uses cache.

## Prerequisites

**Required Modules:**
- `__future__`
- `time`
- `dataclasses`
- `typing`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.retrieval.hopfield_channel`


## Step-by-Step Guide

### Step 1: 'Second search on same profile with same count uses cache.'

```python
'Second search on same profile with same count uses cache.'
```

**Verification:**
```python
assert id(channel._cached_matrix) == cached_matrix_id
```

### Step 2: Assign facts = _make_facts(...)

```python
facts = _make_facts(5)
```

**Verification:**
```python
assert result1 == result2
```

### Step 3: Assign db = FakeDB(...)

```python
db = FakeDB(facts)
```

### Step 4: Assign vs = FakeVectorStore(...)

```python
vs = FakeVectorStore(available=True, count_val=5)
```

### Step 5: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=DIM, enabled=True, cache_ttl_seconds=60.0)
```

### Step 6: Assign channel = HopfieldChannel(...)

```python
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
```

### Step 7: Assign query = _random_embedding(...)

```python
query = _random_embedding(DIM, seed=1)
```

### Step 8: Assign result1 = channel.search(...)

```python
result1 = channel.search(query, 'default')
```

### Step 9: Assign cached_matrix_id = id(...)

```python
cached_matrix_id = id(channel._cached_matrix)
```

### Step 10: Assign result2 = channel.search(...)

```python
result2 = channel.search(query, 'default')
```

**Verification:**
```python
assert id(channel._cached_matrix) == cached_matrix_id
```


## Complete Example

```python
# Workflow
'Second search on same profile with same count uses cache.'
from superlocalmemory.math.hopfield import HopfieldConfig
from superlocalmemory.retrieval.hopfield_channel import HopfieldChannel
facts = _make_facts(5)
db = FakeDB(facts)
vs = FakeVectorStore(available=True, count_val=5)
config = HopfieldConfig(dimension=DIM, enabled=True, cache_ttl_seconds=60.0)
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
query = _random_embedding(DIM, seed=1)
result1 = channel.search(query, 'default')
cached_matrix_id = id(channel._cached_matrix)
result2 = channel.search(query, 'default')
assert id(channel._cached_matrix) == cached_matrix_id
assert result1 == result2
```

## Next Steps


---

*Source: test_hopfield_channel.py:353 | Complexity: Advanced | Last updated: 2026-05-05*