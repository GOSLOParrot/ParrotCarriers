# How To: Recall With Multiple Channels

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test recall with multiple channels

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.fusion`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign facts = value

```python
facts = [_make_fact('f1', 'Alice is an engineer'), _make_fact('f2', 'Bob is a doctor')]
```

**Verification:**
```python
assert len(response.results) == 2
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert response.total_candidates > 0
```

### Step 3: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f1', 0.9), ('f2', 0.5)], bm25_results=[('f2', 0.8), ('f1', 0.3)])
```

### Step 4: Assign response = engine.recall(...)

```python
response = engine.recall('What do they do?', 'default')
```

**Verification:**
```python
assert len(response.results) == 2
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1', 'Alice is an engineer'), _make_fact('f2', 'Bob is a doctor')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f1', 0.9), ('f2', 0.5)], bm25_results=[('f2', 0.8), ('f1', 0.3)])
response = engine.recall('What do they do?', 'default')
assert len(response.results) == 2
assert response.total_candidates > 0
```

## Next Steps


---

*Source: test_engine.py:124 | Complexity: Intermediate | Last updated: 2026-05-05*