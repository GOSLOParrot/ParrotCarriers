# How To: Basic Recall With Semantic Channel

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test basic recall with semantic channel

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
facts = [_make_fact('f1', 'Alice is an engineer')]
```

**Verification:**
```python
assert isinstance(response, RecallResponse)
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert response.query == 'What does Alice do?'
```

### Step 3: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
```

**Verification:**
```python
assert len(response.results) == 1
```

### Step 4: Assign response = engine.recall(...)

```python
response = engine.recall('What does Alice do?', 'default')
```

**Verification:**
```python
assert response.results[0].fact.fact_id == 'f1'
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1', 'Alice is an engineer')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
response = engine.recall('What does Alice do?', 'default')
assert isinstance(response, RecallResponse)
assert response.query == 'What does Alice do?'
assert len(response.results) == 1
assert response.results[0].fact.fact_id == 'f1'
```

## Next Steps


---

*Source: test_engine.py:111 | Complexity: Intermediate | Last updated: 2026-05-05*