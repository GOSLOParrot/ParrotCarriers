# How To: Active Facts Pass Through

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Active zone facts keep full score.

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

### Step 1: 'Active zone facts keep full score.'

```python
'Active zone facts keep full score.'
```

**Verification:**
```python
assert filtered['semantic'][0] == ('f1', 0.8)
```

### Step 2: Assign db = self._make_mock_db(...)

```python
db = self._make_mock_db([{'fact_id': 'f1', 'retention_score': 0.9, 'lifecycle_zone': 'active'}])
```

### Step 3: Assign ff = ForgettingFilter(...)

```python
ff = ForgettingFilter(db, ForgettingConfig())
```

### Step 4: Assign results = value

```python
results = {'semantic': [('f1', 0.8)]}
```

### Step 5: Assign filtered = ff.filter(...)

```python
filtered = ff.filter(results, 'default', None)
```

**Verification:**
```python
assert filtered['semantic'][0] == ('f1', 0.8)
```


## Complete Example

```python
# Workflow
'Active zone facts keep full score.'
from superlocalmemory.retrieval.forgetting_filter import ForgettingFilter
db = self._make_mock_db([{'fact_id': 'f1', 'retention_score': 0.9, 'lifecycle_zone': 'active'}])
ff = ForgettingFilter(db, ForgettingConfig())
results = {'semantic': [('f1', 0.8)]}
filtered = ff.filter(results, 'default', None)
assert filtered['semantic'][0] == ('f1', 0.8)
```

## Next Steps


---

*Source: test_e2e_v33.py:301 | Complexity: Intermediate | Last updated: 2026-05-05*