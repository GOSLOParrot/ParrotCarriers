# How To: Full Consolidation Runs All 6 Steps

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Full consolidation returns results for all 6 steps.

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

### Step 1: 'Full consolidation returns results for all 6 steps.'

```python
'Full consolidation returns results for all 6 steps.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Call _seed_facts()

```python
_seed_facts(tmp_db, 'default', 3)
```

**Verification:**
```python
assert 'compressed' in result
```

### Step 3: Assign result = engine.consolidate(...)

```python
result = engine.consolidate('default', lightweight=False)
```

**Verification:**
```python
assert 'blocks' in result
```


## Complete Example

```python
# Setup
# Fixtures: engine, tmp_db

# Workflow
'Full consolidation returns results for all 6 steps.'
_seed_facts(tmp_db, 'default', 3)
result = engine.consolidate('default', lightweight=False)
assert result['success'] is True
assert 'compressed' in result
assert 'blocks' in result
assert 'promoted' in result
assert 'decayed' in result
assert 'graph_stats' in result
assert 'new_associations' in result
```

## Next Steps


---

*Source: test_consolidation_engine.py:107 | Complexity: Beginner | Last updated: 2026-05-05*