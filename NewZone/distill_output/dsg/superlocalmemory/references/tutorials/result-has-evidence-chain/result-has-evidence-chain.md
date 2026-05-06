# How To: Result Has Evidence Chain

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test result has evidence chain

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
assert len(response.results) > 0
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert isinstance(result.evidence_chain, list)
```

### Step 3: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)], bm25_results=[('f1', 0.7)])
```

**Verification:**
```python
assert len(result.evidence_chain) >= 1
```

### Step 4: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default')
```

**Verification:**
```python
assert len(response.results) > 0
```

### Step 5: Assign result = value

```python
result = response.results[0]
```

**Verification:**
```python
assert isinstance(result.evidence_chain, list)
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)], bm25_results=[('f1', 0.7)])
response = engine.recall('q', 'default')
assert len(response.results) > 0
result = response.results[0]
assert isinstance(result.evidence_chain, list)
assert len(result.evidence_chain) >= 1
```

## Next Steps


---

*Source: test_engine.py:309 | Complexity: Intermediate | Last updated: 2026-05-05*