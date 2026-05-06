# How To: Apply All Creates Pending Outcomes Table

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test apply all creates pending outcomes table

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.storage`

**Setup Required:**
```python
# Fixtures: fresh_dbs
```

## Step-by-Step Guide

### Step 1: Assign unknown = fresh_dbs

```python
learning_db, memory_db = fresh_dbs
```

**Verification:**
```python
assert 'pending_outcomes' in _table_names(memory_db)
```

### Step 2: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

**Verification:**
```python
assert required <= cols
```

### Step 3: Assign cols = set(...)

```python
cols = set(_table_cols(memory_db, 'pending_outcomes'))
```

**Verification:**
```python
assert 'idx_pending_profile_expires' in indexes
```

### Step 4: Assign required = value

```python
required = {'outcome_id', 'profile_id', 'session_id', 'recall_query_id', 'fact_ids_json', 'query_text_hash', 'created_at_ms', 'expires_at_ms', 'signals_json', 'status'}
```

**Verification:**
```python
assert 'idx_pending_status' in indexes
```

### Step 5: Assign indexes = _index_names(...)

```python
indexes = _index_names(memory_db)
```

**Verification:**
```python
assert 'idx_pending_profile_expires' in indexes
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
learning_db, memory_db = fresh_dbs
mr.apply_all(learning_db, memory_db)
assert 'pending_outcomes' in _table_names(memory_db)
cols = set(_table_cols(memory_db, 'pending_outcomes'))
required = {'outcome_id', 'profile_id', 'session_id', 'recall_query_id', 'fact_ids_json', 'query_text_hash', 'created_at_ms', 'expires_at_ms', 'signals_json', 'status'}
assert required <= cols
indexes = _index_names(memory_db)
assert 'idx_pending_profile_expires' in indexes
assert 'idx_pending_status' in indexes
```

## Next Steps


---

*Source: test_migration_runner.py:607 | Complexity: Intermediate | Last updated: 2026-05-05*