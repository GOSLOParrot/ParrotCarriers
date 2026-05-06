# How To: Dry Run On Fully Fresh Dbs

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test dry run on fully fresh dbs

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
assert stats['applied'] == []
```

### Step 2: Assign stats = mr.apply_all(...)

```python
stats = mr.apply_all(learning_db, memory_db, dry_run=True)
```

**Verification:**
```python
assert 'migration_log' not in tables
```

### Step 3: Assign tables = value

```python
tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
```

**Verification:**
```python
assert 'bandit_arms' not in tables
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
learning_db, memory_db = fresh_dbs
stats = mr.apply_all(learning_db, memory_db, dry_run=True)
assert stats['applied'] == []
with sqlite3.connect(learning_db) as conn:
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
assert 'migration_log' not in tables
assert 'bandit_arms' not in tables
```

## Next Steps


---

*Source: test_migration_runner.py:390 | Complexity: Beginner | Last updated: 2026-05-05*