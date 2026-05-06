# How To: Results Sorted Descending

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test results sorted descending

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
facts = [_make_fact('close', embedding=[0.9, 0.1]), _make_fact('far', embedding=[0.1, 0.9])]
```

**Verification:**
```python
assert scores == sorted(scores, reverse=True)
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
results = channel.search([1.0, 0.0], 'default')
```

### Step 5: Assign scores = value

```python
scores = [s for _, s in results]
```

**Verification:**
```python
assert scores == sorted(scores, reverse=True)
```


## Complete Example

```python
# Workflow
facts = [_make_fact('close', embedding=[0.9, 0.1]), _make_fact('far', embedding=[0.1, 0.9])]
db = _mock_db(facts)
channel = SemanticChannel(db)
results = channel.search([1.0, 0.0], 'default')
scores = [s for _, s in results]
assert scores == sorted(scores, reverse=True)
```

## Next Steps


---

*Source: test_semantic_channel.py:201 | Complexity: Intermediate | Last updated: 2026-05-05*