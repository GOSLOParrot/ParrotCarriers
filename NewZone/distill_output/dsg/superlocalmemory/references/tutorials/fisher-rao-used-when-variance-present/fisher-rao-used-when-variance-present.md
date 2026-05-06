# How To: Fisher Rao Used When Variance Present

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test fisher rao used when variance present

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.semantic_channel`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign facts = value

```python
facts = [_make_fact('f1', embedding=[1.0, 0.0], fisher_variance=[0.1, 0.1])]
```

**Verification:**
```python
assert len(results) == 1
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert results[0][0] == 'f1'
```

### Step 3: Assign channel = SemanticChannel(...)

```python
channel = SemanticChannel(db, fisher_temperature=15.0)
```

**Verification:**
```python
assert results[0][1] == pytest.approx(1.0, abs=0.001)
```

### Step 4: Assign results = channel.search(...)

```python
results = channel.search([1.0, 0.0], 'default')
```

**Verification:**
```python
assert len(results) == 1
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1', embedding=[1.0, 0.0], fisher_variance=[0.1, 0.1])]
db = _mock_db(facts)
channel = SemanticChannel(db, fisher_temperature=15.0)
results = channel.search([1.0, 0.0], 'default')
assert len(results) == 1
assert results[0][0] == 'f1'
assert results[0][1] == pytest.approx(1.0, abs=0.001)
```

## Next Steps


---

*Source: test_semantic_channel.py:176 | Complexity: Intermediate | Last updated: 2026-05-05*