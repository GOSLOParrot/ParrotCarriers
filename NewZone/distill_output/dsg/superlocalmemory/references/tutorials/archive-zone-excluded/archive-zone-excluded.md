# How To: Archive Zone Excluded

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Archive zone facts are removed like forgotten.

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

### Step 1: 'Archive zone facts are removed like forgotten.'

```python
'Archive zone facts are removed like forgotten.'
```

**Verification:**
```python
assert len(filtered['semantic']) == 0
```

### Step 2: Assign db = self._make_mock_db(...)

```python
db = self._make_mock_db([{'fact_id': 'f6', 'retention_score': 0.1, 'lifecycle_zone': 'archive'}])
```

### Step 3: Assign ff = ForgettingFilter(...)

```python
ff = ForgettingFilter(db, ForgettingConfig())
```

### Step 4: Assign results = value

```python
results = {'semantic': [('f6', 0.9)]}
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
'Archive zone facts are removed like forgotten.'
from superlocalmemory.retrieval.forgetting_filter import ForgettingFilter
db = self._make_mock_db([{'fact_id': 'f6', 'retention_score': 0.1, 'lifecycle_zone': 'archive'}])
ff = ForgettingFilter(db, ForgettingConfig())
results = {'semantic': [('f6', 0.9)]}
filtered = ff.filter(results, 'default', None)
assert len(filtered['semantic']) == 0
```

## Next Steps


---

*Source: test_e2e_v33.py:380 | Complexity: Intermediate | Last updated: 2026-05-05*