# How To: Forgotten Facts Removed

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Forgotten zone facts are excluded from results entirely.

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

### Step 1: 'Forgotten zone facts are excluded from results entirely.'

```python
'Forgotten zone facts are excluded from results entirely.'
```

**Verification:**
```python
assert len(filtered['semantic']) == 0
```

### Step 2: Assign db = self._make_mock_db(...)

```python
db = self._make_mock_db([{'fact_id': 'f3', 'retention_score': 0.01, 'lifecycle_zone': 'forgotten'}])
```

### Step 3: Assign ff = ForgettingFilter(...)

```python
ff = ForgettingFilter(db, ForgettingConfig())
```

### Step 4: Assign results = value

```python
results = {'semantic': [('f3', 0.9)]}
```

### Step 5: Assign filtered = ff.filter(...)

```python
filtered = ff.filter(results, 'default', None)
```

**Verification:**
```python
assert len(filtered['semantic']) == 0
```


## Complete Example

```python
# Workflow
'Forgotten zone facts are excluded from results entirely.'
from superlocalmemory.retrieval.forgetting_filter import ForgettingFilter
db = self._make_mock_db([{'fact_id': 'f3', 'retention_score': 0.01, 'lifecycle_zone': 'forgotten'}])
ff = ForgettingFilter(db, ForgettingConfig())
results = {'semantic': [('f3', 0.9)]}
filtered = ff.filter(results, 'default', None)
assert len(filtered['semantic']) == 0
```

## Next Steps


---

*Source: test_e2e_v33.py:328 | Complexity: Intermediate | Last updated: 2026-05-05*