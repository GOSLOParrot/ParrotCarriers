# How To: Temporal Only Works

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: A single temporal channel is sufficient to produce results.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'A single temporal channel is sufficient to produce results.'

```python
'A single temporal channel is sufficient to produce results.'
```

**Verification:**
```python
assert len(response.results) == 1
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f1', 'Last week the team completed the migration to the new database')]
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, temporal_results=[('f1', 0.6)])
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
'A single temporal channel is sufficient to produce results.'
facts = [_make_fact('f1', 'Last week the team completed the migration to the new database')]
db = _mock_db(facts)
engine = _build_engine(db=db, temporal_results=[('f1', 0.6)])
response = engine.recall('q', 'default')
assert len(response.results) == 1
```

## Next Steps


---

*Source: test_retrieval_integration.py:170 | Complexity: Intermediate | Last updated: 2026-05-05*