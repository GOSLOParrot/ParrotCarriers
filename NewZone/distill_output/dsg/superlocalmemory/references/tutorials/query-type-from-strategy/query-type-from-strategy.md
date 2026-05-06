# How To: Query Type From Strategy

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test query type from strategy

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
facts = [_make_fact('f1')]
```

**Verification:**
```python
assert response.query_type == 'temporal'
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 3: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
```

### Step 4: Assign response = engine.recall(...)

```python
response = engine.recall('When did Alice start?', 'default')
```

**Verification:**
```python
assert response.query_type == 'temporal'
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
response = engine.recall('When did Alice start?', 'default')
assert response.query_type == 'temporal'
```

## Next Steps


---

*Source: test_engine.py:293 | Complexity: Intermediate | Last updated: 2026-05-05*