# How To: Promote Filters Expired Facts

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts with valid_until in the past are NOT promoted (L12).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.consolidation_engine`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine, tmp_db
```

## Step-by-Step Guide

### Step 1: 'Facts with valid_until in the past are NOT promoted (L12).'

```python
'Facts with valid_until in the past are NOT promoted (L12).'
```

**Verification:**
```python
assert fact.lifecycle.value == 'active'
```

### Step 2: Assign ids = _seed_facts(...)

```python
ids = _seed_facts(tmp_db, 'default', 1)
```

### Step 3: Assign fid = value

```python
fid = ids[0]
```

### Step 4: Call tmp_db.store_temporal_validity()

```python
tmp_db.store_temporal_validity(fid, 'default', valid_until='2020-01-01T00:00:00')
```

### Step 5: Assign result = engine._step3_promote(...)

```python
result = engine._step3_promote('default')
```

### Step 6: Assign fact = tmp_db.get_fact(...)

```python
fact = tmp_db.get_fact(fid)
```

**Verification:**
```python
assert fact.lifecycle.value == 'active'
```

### Step 7: Call tmp_db.execute()

```python
tmp_db.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id) VALUES (?, ?, ?)', (_new_id(), fid, 'default'))
```


## Complete Example

```python
# Setup
# Fixtures: engine, tmp_db

# Workflow
'Facts with valid_until in the past are NOT promoted (L12).'
ids = _seed_facts(tmp_db, 'default', 1)
fid = ids[0]
from superlocalmemory.storage.models import _new_id
for _ in range(5):
    tmp_db.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id) VALUES (?, ?, ?)', (_new_id(), fid, 'default'))
tmp_db.store_temporal_validity(fid, 'default', valid_until='2020-01-01T00:00:00')
result = engine._step3_promote('default')
fact = tmp_db.get_fact(fid)
assert fact.lifecycle.value == 'active'
```

## Next Steps


---

*Source: test_consolidation_engine.py:297 | Complexity: Intermediate | Last updated: 2026-05-05*