# How To: Promote Requires Min Access

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts below access threshold are NOT promoted.

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

### Step 1: 'Facts below access threshold are NOT promoted.'

```python
'Facts below access threshold are NOT promoted.'
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

### Step 4: Call tmp_db.execute()

```python
tmp_db.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id) VALUES (?, ?, ?)', (_new_id(), fid, 'default'))
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


## Complete Example

```python
# Setup
# Fixtures: engine, tmp_db

# Workflow
'Facts below access threshold are NOT promoted.'
ids = _seed_facts(tmp_db, 'default', 1)
fid = ids[0]
from superlocalmemory.storage.models import _new_id
tmp_db.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id) VALUES (?, ?, ?)', (_new_id(), fid, 'default'))
result = engine._step3_promote('default')
fact = tmp_db.get_fact(fid)
assert fact.lifecycle.value == 'active'
```

## Next Steps


---

*Source: test_consolidation_engine.py:337 | Complexity: Intermediate | Last updated: 2026-05-05*