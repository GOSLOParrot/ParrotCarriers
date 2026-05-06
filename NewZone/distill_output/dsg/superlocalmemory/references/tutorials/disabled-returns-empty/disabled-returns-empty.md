# How To: Disabled Returns Empty

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test disabled returns empty

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
facts = _make_facts(10)
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
vs = FakeVectorStore(available=True, count_val=10)
```

### Step 4: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=DIM, enabled=False)
```

### Step 5: Assign channel = HopfieldChannel(...)

```python
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
```

### Step 6: Assign query = _random_embedding(...)

```python
query = _random_embedding(DIM, seed=1)
```

### Step 7: Assign result = channel.search(...)

```python
result = channel.search(query, 'default')
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
facts = _make_facts(10)
db = FakeDB(facts)
vs = FakeVectorStore(available=True, count_val=10)
config = HopfieldConfig(dimension=DIM, enabled=False)
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
query = _random_embedding(DIM, seed=1)
result = channel.search(query, 'default')
assert result == []
```

## Next Steps


---

*Source: test_hopfield_channel.py:189 | Complexity: Intermediate | Last updated: 2026-05-05*