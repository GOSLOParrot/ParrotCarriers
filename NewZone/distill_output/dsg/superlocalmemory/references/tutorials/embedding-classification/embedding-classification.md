# How To: Embedding Classification

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test embedding classification

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `unittest.mock`
- `pytest`
- `superlocalmemory.encoding.type_router`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign embedder = self._mock_embedder(...)

```python
embedder = self._mock_embedder()
```

**Verification:**
```python
assert isinstance(result, FactType)
```

### Step 2: Assign router = TypeRouter(...)

```python
router = TypeRouter(mode=Mode.A, embedder=embedder)
```

### Step 3: Assign fact = AtomicFact(...)

```python
fact = AtomicFact(fact_id='f1', content='The capital of France is Paris')
```

### Step 4: Assign result = router.classify(...)

```python
result = router.classify(fact)
```

**Verification:**
```python
assert isinstance(result, FactType)
```


## Complete Example

```python
# Workflow
embedder = self._mock_embedder()
router = TypeRouter(mode=Mode.A, embedder=embedder)
fact = AtomicFact(fact_id='f1', content='The capital of France is Paris')
result = router.classify(fact)
assert isinstance(result, FactType)
```

## Next Steps


---

*Source: test_type_router.py:113 | Complexity: Intermediate | Last updated: 2026-05-05*