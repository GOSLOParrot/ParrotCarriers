# How To: Apply All Extends Model State Columns

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test apply all extends model state columns

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
assert required <= cols
```

### Step 2: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

**Verification:**
```python
assert 'idx_model_active_one' in indexes
```

### Step 3: Assign cols = set(...)

```python
cols = set(_table_cols(learning_db, 'learning_model_state'))
```

**Verification:**
```python
assert 'idx_model_candidate_one' in indexes
```

### Step 4: Assign required = value

```python
required = {'is_previous', 'is_rollback', 'is_candidate', 'shadow_results_json', 'promoted_at', 'rollback_reason'}
```

**Verification:**
```python
assert required <= cols
```

### Step 5: Assign indexes = _index_names(...)

```python
indexes = _index_names(learning_db)
```

**Verification:**
```python
assert 'idx_model_active_one' in indexes
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
learning_db, memory_db = fresh_dbs
mr.apply_all(learning_db, memory_db)
cols = set(_table_cols(learning_db, 'learning_model_state'))
required = {'is_previous', 'is_rollback', 'is_candidate', 'shadow_results_json', 'promoted_at', 'rollback_reason'}
assert required <= cols
indexes = _index_names(learning_db)
assert 'idx_model_active_one' in indexes
assert 'idx_model_candidate_one' in indexes
```

## Next Steps


---

*Source: test_migration_runner.py:625 | Complexity: Intermediate | Last updated: 2026-05-05*