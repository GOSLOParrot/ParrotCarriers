# How To: Recall Limit Respected

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test recall limit respected

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
facts = [_make_fact(f'f{i}') for i in range(20)]
```

**Verification:**
```python
assert len(response.results) <= 5
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 3: Assign sem_results = value

```python
sem_results = [(f'f{i}', 0.9 - i * 0.01) for i in range(20)]
```

### Step 4: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=sem_results)
```

### Step 5: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default', limit=5)
```

**Verification:**
```python
assert len(response.results) <= 5
```


## Complete Example

```python
# Workflow
facts = [_make_fact(f'f{i}') for i in range(20)]
db = _mock_db(facts)
sem_results = [(f'f{i}', 0.9 - i * 0.01) for i in range(20)]
engine = _build_engine(db=db, semantic_results=sem_results)
response = engine.recall('q', 'default', limit=5)
assert len(response.results) <= 5
```

## Next Steps


---

*Source: test_engine.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*