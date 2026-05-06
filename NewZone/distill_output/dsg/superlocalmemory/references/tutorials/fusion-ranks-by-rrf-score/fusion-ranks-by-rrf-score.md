# How To: Fusion Ranks By Rrf Score

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Facts appearing in more channels should rank higher via RRF.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Facts appearing in more channels should rank higher via RRF.'

```python
'Facts appearing in more channels should rank higher via RRF.'
```

**Verification:**
```python
assert len(response.results) == 2
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f_multi', 'Alice is an engineer working on multiple critical projects'), _make_fact('f_single', 'Bob mentioned he likes coffee during the morning standup')]
```

**Verification:**
```python
assert response.results[0].fact.fact_id == 'f_multi'
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f_multi', 0.9), ('f_single', 0.3)], bm25_results=[('f_multi', 0.8)])
```

### Step 5: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default')
```

**Verification:**
```python
assert len(response.results) == 2
```


## Complete Example

```python
# Workflow
'Facts appearing in more channels should rank higher via RRF.'
facts = [_make_fact('f_multi', 'Alice is an engineer working on multiple critical projects'), _make_fact('f_single', 'Bob mentioned he likes coffee during the morning standup')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f_multi', 0.9), ('f_single', 0.3)], bm25_results=[('f_multi', 0.8)])
response = engine.recall('q', 'default')
assert len(response.results) == 2
assert response.results[0].fact.fact_id == 'f_multi'
```

## Next Steps


---

*Source: test_retrieval_integration.py:178 | Complexity: Intermediate | Last updated: 2026-05-05*