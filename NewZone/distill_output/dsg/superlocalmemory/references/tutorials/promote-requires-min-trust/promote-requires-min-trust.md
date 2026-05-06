# How To: Promote Requires Min Trust

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts below trust threshold are NOT promoted.

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
# Fixtures: tmp_db, slm_config
```

## Step-by-Step Guide

### Step 1: 'Facts below trust threshold are NOT promoted.'

```python
'Facts below trust threshold are NOT promoted.'
```

**Verification:**
```python
assert fact.lifecycle.value == 'active'
```

### Step 2: Assign strict_config = ConsolidationConfig(...)

```python
strict_config = ConsolidationConfig(enabled=True, promotion_min_access=1, promotion_min_trust=0.99)
```

### Step 3: Assign eng = ConsolidationEngine(...)

```python
eng = ConsolidationEngine(db=tmp_db, config=strict_config, slm_config=slm_config)
```

### Step 4: Assign ids = _seed_facts(...)

```python
ids = _seed_facts(tmp_db, 'default', 1)
```

### Step 5: Assign fid = value

```python
fid = ids[0]
```

### Step 6: Assign result = eng._step3_promote(...)

```python
result = eng._step3_promote('default')
```

### Step 7: Assign fact = tmp_db.get_fact(...)

```python
fact = tmp_db.get_fact(fid)
```

**Verification:**
```python
assert fact.lifecycle.value == 'active'
```

### Step 8: Call tmp_db.execute()

```python
tmp_db.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id) VALUES (?, ?, ?)', (_new_id(), fid, 'default'))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_db, slm_config

# Workflow
'Facts below trust threshold are NOT promoted.'
strict_config = ConsolidationConfig(enabled=True, promotion_min_access=1, promotion_min_trust=0.99)
eng = ConsolidationEngine(db=tmp_db, config=strict_config, slm_config=slm_config)
ids = _seed_facts(tmp_db, 'default', 1)
fid = ids[0]
from superlocalmemory.storage.models import _new_id
for _ in range(5):
    tmp_db.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id) VALUES (?, ?, ?)', (_new_id(), fid, 'default'))
result = eng._step3_promote('default')
fact = tmp_db.get_fact(fid)
assert fact.lifecycle.value == 'active'
```

## Next Steps


---

*Source: test_consolidation_engine.py:354 | Complexity: Advanced | Last updated: 2026-05-05*