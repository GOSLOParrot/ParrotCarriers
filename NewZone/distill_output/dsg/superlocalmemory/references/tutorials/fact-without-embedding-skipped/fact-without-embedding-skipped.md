# How To: Fact Without Embedding Skipped

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test fact without embedding skipped

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
facts = [_make_fact('f1', embedding=None)]
```

**Verification:**
```python
assert results == []
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

**Verification:**
```python
assert results == []
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1', embedding=None)]
db = _mock_db(facts)
channel = SemanticChannel(db)
results = channel.search([1.0, 0.0], 'default')
assert results == []
```

## Next Steps


---

*Source: test_semantic_channel.py:150 | Complexity: Intermediate | Last updated: 2026-05-05*