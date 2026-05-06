# How To: Apply All On Fresh Db Applies All

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test apply all on fresh db applies all

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
assert stats['applied']
```

### Step 2: Assign stats = mr.apply_all(...)

```python
stats = mr.apply_all(learning_db, memory_db)
```

**Verification:**
```python
assert stats['failed'] == [] or stats['failed'] == 0 or (not stats['failed'])
```

### Step 3: Assign log_learning = _log_rows(...)

```python
log_learning = _log_rows(learning_db)
```

**Verification:**
```python
assert len(stats['applied']) == 9
```

### Step 4: Assign log_memory = _log_rows(...)

```python
log_memory = _log_rows(memory_db)
```

**Verification:**
```python
assert 'M003_migration_log' in names_learning
```

### Step 5: Assign names_learning = value

```python
names_learning = [r[0] for r in log_learning]
```

**Verification:**
```python
assert 'M001_add_signal_features_columns' in names_learning
```

### Step 6: Assign names_memory = value

```python
names_memory = [r[0] for r in log_memory]
```

**Verification:**
```python
assert 'M002_model_state_history' in names_learning
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
learning_db, memory_db = fresh_dbs
stats = mr.apply_all(learning_db, memory_db)
assert stats['applied']
assert stats['failed'] == [] or stats['failed'] == 0 or (not stats['failed'])
assert len(stats['applied']) == 9
log_learning = _log_rows(learning_db)
log_memory = _log_rows(memory_db)
names_learning = [r[0] for r in log_learning]
names_memory = [r[0] for r in log_memory]
assert 'M003_migration_log' in names_learning
assert 'M001_add_signal_features_columns' in names_learning
assert 'M002_model_state_history' in names_learning
assert 'M005_bandit_tables' in names_learning
assert 'M009_model_lineage' in names_learning
assert 'M010_evolution_config' in names_learning
assert 'M004_cross_platform_sync_log' in names_memory
assert 'M007_pending_outcomes' in names_memory
```

## Next Steps


---

*Source: test_migration_runner.py:134 | Complexity: Intermediate | Last updated: 2026-05-05*