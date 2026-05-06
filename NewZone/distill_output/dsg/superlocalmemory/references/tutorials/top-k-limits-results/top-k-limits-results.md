# How To: Top K Limits Results

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test top k limits results

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.semantic_channel`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign facts = value

```python
facts = [_make_fact(f'f{i}', embedding=[float(i), 0.0]) for i in range(1, 20)]
```

**Verification:**
```python
assert len(results) <= 5
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 3: Assign channel = SemanticChannel(...)

```python
channel = SemanticChannel(db)
```

### Step 4: Assign results = channel.search(...)

```python
results = channel.search([1.0, 0.0], 'default', top_k=5)
```

**Verification:**
```python
assert len(results) <= 5
```


## Complete Example

```python
# Workflow
facts = [_make_fact(f'f{i}', embedding=[float(i), 0.0]) for i in range(1, 20)]
db = _mock_db(facts)
channel = SemanticChannel(db)
results = channel.search([1.0, 0.0], 'default', top_k=5)
assert len(results) <= 5
```

## Next Steps


---

*Source: test_semantic_channel.py:192 | Complexity: Intermediate | Last updated: 2026-05-05*