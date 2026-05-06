# How To: Large Scale Triggers Prefilter

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test large scale triggers prefilter

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

### Step 1: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=DIM, enabled=True, prefilter_threshold=5, prefilter_candidates=3)
```

**Verification:**
```python
assert isinstance(result, list)
```

### Step 2: Assign facts = _make_facts(...)

```python
facts = _make_facts(20)
```

**Verification:**
```python
assert result_ids.issubset(candidate_ids), f'Result IDs {result_ids} not subset of KNN candidates {candidate_ids}'
```

### Step 3: Assign db = FakeDB(...)

```python
db = FakeDB(facts)
```

### Step 4: Assign knn_results = value

```python
knn_results = [(f'fact_{i}', 0.9 - i * 0.1) for i in range(3)]
```

### Step 5: Assign vs = FakeVectorStore(...)

```python
vs = FakeVectorStore(available=True, count_val=20, search_results=knn_results)
```

### Step 6: Assign channel = HopfieldChannel(...)

```python
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
```

### Step 7: Assign query = _random_embedding(...)

```python
query = _random_embedding(DIM, seed=42)
```

### Step 8: Assign result = channel.search(...)

```python
result = channel.search(query, 'default')
```

**Verification:**
```python
assert isinstance(result, list)
```

### Step 9: Assign result_ids = value

```python
result_ids = {fid for fid, _ in result}
```

### Step 10: Assign candidate_ids = value

```python
candidate_ids = {fid for fid, _ in knn_results}
```

**Verification:**
```python
assert result_ids.issubset(candidate_ids), f'Result IDs {result_ids} not subset of KNN candidates {candidate_ids}'
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig
from superlocalmemory.retrieval.hopfield_channel import HopfieldChannel
config = HopfieldConfig(dimension=DIM, enabled=True, prefilter_threshold=5, prefilter_candidates=3)
facts = _make_facts(20)
db = FakeDB(facts)
knn_results = [(f'fact_{i}', 0.9 - i * 0.1) for i in range(3)]
vs = FakeVectorStore(available=True, count_val=20, search_results=knn_results)
channel = HopfieldChannel(db=db, vector_store=vs, config=config)
query = _random_embedding(DIM, seed=42)
result = channel.search(query, 'default')
assert isinstance(result, list)
result_ids = {fid for fid, _ in result}
candidate_ids = {fid for fid, _ in knn_results}
assert result_ids.issubset(candidate_ids), f'Result IDs {result_ids} not subset of KNN candidates {candidate_ids}'
```

## Next Steps


---

*Source: test_hopfield_channel.py:236 | Complexity: Advanced | Last updated: 2026-05-05*