# How To: No Retention Data Keeps Fact

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Facts with no retention row yet are kept as-is (new memories).

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `uuid`
- `datetime`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.strategy`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage`
- `superlocalmemory.storage`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.forgetting_filter`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.strategy`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.strategy`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.strategy`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.strategy`
- `superlocalmemory.storage.migration_v33`
- `superlocalmemory.storage.migration_v33`
- `superlocalmemory.storage.migration_v33`
- `superlocalmemory.storage.migration_v33`
- `superlocalmemory.storage.migration_v33`
- `superlocalmemory.core.engine_wiring`
- `superlocalmemory.core.engine_wiring`
- `superlocalmemory.core.engine_wiring`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Facts with no retention row yet are kept as-is (new memories).'

```python
'Facts with no retention row yet are kept as-is (new memories).'
```

**Verification:**
```python
assert filtered['semantic'][0] == ('new_fact', 0.7)
```

### Step 2: Assign db = self._make_mock_db(...)

```python
db = self._make_mock_db([])
```

### Step 3: Assign ff = ForgettingFilter(...)

```python
ff = ForgettingFilter(db, ForgettingConfig())
```

### Step 4: Assign results = value

```python
results = {'semantic': [('new_fact', 0.7)]}
```

### Step 5: Assign filtered = ff.filter(...)

```python
filtered = ff.filter(results, 'default', None)
```

**Verification:**
```python
assert filtered['semantic'][0] == ('new_fact', 0.7)
```


## Complete Example

```python
# Workflow
'Facts with no retention row yet are kept as-is (new memories).'
from superlocalmemory.retrieval.forgetting_filter import ForgettingFilter
db = self._make_mock_db([])
ff = ForgettingFilter(db, ForgettingConfig())
results = {'semantic': [('new_fact', 0.7)]}
filtered = ff.filter(results, 'default', None)
assert filtered['semantic'][0] == ('new_fact', 0.7)
```

## Next Steps


---

*Source: test_e2e_v33.py:356 | Complexity: Intermediate | Last updated: 2026-05-05*