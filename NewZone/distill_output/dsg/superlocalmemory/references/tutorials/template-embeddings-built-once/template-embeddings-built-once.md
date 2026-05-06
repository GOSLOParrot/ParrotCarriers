# How To: Template Embeddings Built Once

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test template embeddings built once

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
assert router._template_embeddings is not None
```

### Step 2: Assign router = TypeRouter(...)

```python
router = TypeRouter(mode=Mode.A, embedder=embedder)
```

### Step 3: Assign f1 = AtomicFact(...)

```python
f1 = AtomicFact(fact_id='f1', content='fact about world')
```

### Step 4: Assign f2 = AtomicFact(...)

```python
f2 = AtomicFact(fact_id='f2', content='another fact')
```

### Step 5: Call router.classify()

```python
router.classify(f1)
```

**Verification:**
```python
assert router._template_embeddings is not None
```

### Step 6: Call router.classify()

```python
router.classify(f2)
```


## Complete Example

```python
# Workflow
embedder = self._mock_embedder()
router = TypeRouter(mode=Mode.A, embedder=embedder)
f1 = AtomicFact(fact_id='f1', content='fact about world')
f2 = AtomicFact(fact_id='f2', content='another fact')
router.classify(f1)
assert router._template_embeddings is not None
router.classify(f2)
```

## Next Steps


---

*Source: test_type_router.py:121 | Complexity: Intermediate | Last updated: 2026-05-05*