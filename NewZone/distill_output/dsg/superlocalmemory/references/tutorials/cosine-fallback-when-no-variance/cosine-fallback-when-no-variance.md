# How To: Cosine Fallback When No Variance

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test cosine fallback when no variance

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
facts = [_make_fact('f1', embedding=[1.0, 0.0]), _make_fact('f2', embedding=[0.0, 1.0])]
```

**Verification:**
```python
assert len(results) == 2
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert results[0][0] == 'f1'
```

### Step 3: Assign channel = SemanticChannel(...)

```python
channel = SemanticChannel(db)
```

**Verification:**
```python
assert results[0][1] > results[1][1]
```

### Step 4: Assign results = channel.search(...)

```python
results = channel.search([1.0, 0.0], 'default', top_k=10)
```

**Verification:**
```python
assert len(results) == 2
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1', embedding=[1.0, 0.0]), _make_fact('f2', embedding=[0.0, 1.0])]
db = _mock_db(facts)
channel = SemanticChannel(db)
results = channel.search([1.0, 0.0], 'default', top_k=10)
assert len(results) == 2
assert results[0][0] == 'f1'
assert results[0][1] > results[1][1]
```

## Next Steps


---

*Source: test_semantic_channel.py:164 | Complexity: Intermediate | Last updated: 2026-05-05*