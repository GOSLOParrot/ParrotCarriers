# How To: Warm Zone Gets 07 Weight

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Warm zone facts get 0.7x weight.

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

### Step 1: 'Warm zone facts get 0.7x weight.'

```python
'Warm zone facts get 0.7x weight.'
```

**Verification:**
```python
assert abs(filtered['bm25'][0][1] - 0.7) < 0.01
```

### Step 2: Assign db = self._make_mock_db(...)

```python
db = self._make_mock_db([{'fact_id': 'f5', 'retention_score': 0.5, 'lifecycle_zone': 'warm'}])
```

### Step 3: Assign ff = ForgettingFilter(...)

```python
ff = ForgettingFilter(db, ForgettingConfig())
```

### Step 4: Assign results = value

```python
results = {'bm25': [('f5', 1.0)]}
```

### Step 5: Assign filtered = ff.filter(...)

```python
filtered = ff.filter(results, 'default', None)
```

**Verification:**
```python
assert abs(filtered['bm25'][0][1] - 0.7) < 0.01
```


## Complete Example

```python
# Workflow
'Warm zone facts get 0.7x weight.'
from superlocalmemory.retrieval.forgetting_filter import ForgettingFilter
db = self._make_mock_db([{'fact_id': 'f5', 'retention_score': 0.5, 'lifecycle_zone': 'warm'}])
ff = ForgettingFilter(db, ForgettingConfig())
results = {'bm25': [('f5', 1.0)]}
filtered = ff.filter(results, 'default', None)
assert abs(filtered['bm25'][0][1] - 0.7) < 0.01
```

## Next Steps


---

*Source: test_e2e_v33.py:367 | Complexity: Intermediate | Last updated: 2026-05-05*