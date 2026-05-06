# How To: Dimension Mismatch Returns Empty

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test dimension mismatch returns empty

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

### Step 1: Assign facts = _make_facts(...)

```python
facts = _make_facts(5, d=DIM)
```

**Verification:**
```python
assert result == []
```

### Step 2: Assign db = FakeDB(...)

```python
db = FakeDB(facts)
```

### Step 3: Assign vs = FakeVectorStore(...)

```python
vs = FakeVectorStore(available=True, count_val=5)
```

### Step 4: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=DIM, enabled=True)
```

### Step 5: Assign channel = HopfieldChannel(...)

```python
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
```

### Step 6: Assign wrong_dim_query = _random_embedding(...)

```python
wrong_dim_query = _random_embedding(384, seed=1)
```

### Step 7: Assign result = channel.search(...)

```python
result = channel.search(wrong_dim_query, 'default')
```

**Verification:**
```python
assert result == []
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig
from superlocalmemory.retrieval.hopfield_channel import HopfieldChannel
facts = _make_facts(5, d=DIM)
db = FakeDB(facts)
vs = FakeVectorStore(available=True, count_val=5)
config = HopfieldConfig(dimension=DIM, enabled=True)
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
wrong_dim_query = _random_embedding(384, seed=1)
result = channel.search(wrong_dim_query, 'default')
assert result == []
```

## Next Steps


---

*Source: test_hopfield_channel.py:212 | Complexity: Intermediate | Last updated: 2026-05-05*