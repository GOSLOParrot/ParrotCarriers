# How To: Recall Facts Returns Tuples

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: recall_facts must return list of (AtomicFact, float) tuples.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'recall_facts must return list of (AtomicFact, float) tuples.'

```python
'recall_facts must return list of (AtomicFact, float) tuples.'
```

**Verification:**
```python
assert len(pairs) == 1
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f1', 'Alice is a senior engineer building production systems at scale')]
```

**Verification:**
```python
assert isinstance(fact_obj, AtomicFact)
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert isinstance(score, float)
```

### Step 4: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
```

**Verification:**
```python
assert fact_obj.fact_id == 'f1'
```

### Step 5: Assign pairs = engine.recall_facts(...)

```python
pairs = engine.recall_facts('q', 'default', top_k=10)
```

**Verification:**
```python
assert len(pairs) == 1
```

### Step 6: Assign unknown = value

```python
fact_obj, score = pairs[0]
```

**Verification:**
```python
assert isinstance(fact_obj, AtomicFact)
```


## Complete Example

```python
# Workflow
'recall_facts must return list of (AtomicFact, float) tuples.'
facts = [_make_fact('f1', 'Alice is a senior engineer building production systems at scale')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
pairs = engine.recall_facts('q', 'default', top_k=10)
assert len(pairs) == 1
fact_obj, score = pairs[0]
assert isinstance(fact_obj, AtomicFact)
assert isinstance(score, float)
assert fact_obj.fact_id == 'f1'
```

## Next Steps


---

*Source: test_retrieval_integration.py:312 | Complexity: Intermediate | Last updated: 2026-05-05*