# How To: Single Fact Retrieval

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test single fact retrieval

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
facts = _make_facts(1)
```

**Verification:**
```python
assert len(result) == 1
```

### Step 2: Assign db = FakeDB(...)

```python
db = FakeDB(facts)
```

**Verification:**
```python
assert fid == 'fact_0'
```

### Step 3: Assign vs = FakeVectorStore(...)

```python
vs = FakeVectorStore(available=True, count_val=1)
```

**Verification:**
```python
assert score > 0.0
```

### Step 4: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=DIM, enabled=True)
```

### Step 5: Assign channel = HopfieldChannel(...)

```python
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
```

### Step 6: Assign query = value

```python
query = facts[0].embedding
```

### Step 7: Assign result = channel.search(...)

```python
result = channel.search(query, 'default')
```

**Verification:**
```python
assert len(result) == 1
```

### Step 8: Assign unknown = value

```python
fid, score = result[0]
```

**Verification:**
```python
assert fid == 'fact_0'
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig
from superlocalmemory.retrieval.hopfield_channel import HopfieldChannel
facts = _make_facts(1)
db = FakeDB(facts)
vs = FakeVectorStore(available=True, count_val=1)
config = HopfieldConfig(dimension=DIM, enabled=True)
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
query = facts[0].embedding
result = channel.search(query, 'default')
assert len(result) == 1
fid, score = result[0]
assert fid == 'fact_0'
assert score > 0.0
```

## Next Steps


---

*Source: test_hopfield_channel.py:162 | Complexity: Advanced | Last updated: 2026-05-05*