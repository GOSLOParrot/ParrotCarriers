# How To: Entity Graph Enhances Bm25

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: V3.4.12: entity_graph is a signal enhancer, not independent channel.
It boosts BM25/semantic candidates by graph proximity.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'V3.4.12: entity_graph is a signal enhancer, not independent channel.\n        It boosts BM25/semantic candidates by graph proximity.'

```python
'V3.4.12: entity_graph is a signal enhancer, not independent channel.\n        It boosts BM25/semantic candidates by graph proximity.'
```

**Verification:**
```python
assert len(response.results) == 1
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f1', 'Charlie mentioned the product roadmap in the planning session')]
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, bm25_results=[('f1', 0.8)], entity_results=[('f1', 0.7)])
```

### Step 5: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default')
```

**Verification:**
```python
assert len(response.results) == 1
```


## Complete Example

```python
# Workflow
'V3.4.12: entity_graph is a signal enhancer, not independent channel.\n        It boosts BM25/semantic candidates by graph proximity.'
facts = [_make_fact('f1', 'Charlie mentioned the product roadmap in the planning session')]
db = _mock_db(facts)
engine = _build_engine(db=db, bm25_results=[('f1', 0.8)], entity_results=[('f1', 0.7)])
response = engine.recall('q', 'default')
assert len(response.results) == 1
```

## Next Steps


---

*Source: test_retrieval_integration.py:159 | Complexity: Intermediate | Last updated: 2026-05-05*