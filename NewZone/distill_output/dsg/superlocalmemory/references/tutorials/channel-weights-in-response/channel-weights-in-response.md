# How To: Channel Weights In Response

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test channel weights in response

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
assert isinstance(response.channel_weights, dict)
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert len(response.channel_weights) > 0
```

### Step 3: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
```

### Step 4: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default')
```

**Verification:**
```python
assert isinstance(response.channel_weights, dict)
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f1', 0.9)])
response = engine.recall('q', 'default')
assert isinstance(response.channel_weights, dict)
assert len(response.channel_weights) > 0
```

## Next Steps


---

*Source: test_engine.py:301 | Complexity: Intermediate | Last updated: 2026-05-05*