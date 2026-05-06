# How To: Status Partial Complete

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test status partial complete

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
assert s['M005_bandit_tables'] == 'failed'
```

### Step 2: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

### Step 3: Assign s = mr.status(...)

```python
s = mr.status(learning_db, memory_db)
```

**Verification:**
```python
assert s['M005_bandit_tables'] == 'failed'
```

### Step 4: Call conn.execute()

```python
conn.execute("UPDATE migration_log SET status='failed' WHERE name=?", ('M005_bandit_tables',))
```

### Step 5: Call conn.commit()

```python
conn.commit()
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
learning_db, memory_db = fresh_dbs
mr.apply_all(learning_db, memory_db)
with sqlite3.connect(learning_db) as conn:
    conn.execute("UPDATE migration_log SET status='failed' WHERE name=?", ('M005_bandit_tables',))
    conn.commit()
s = mr.status(learning_db, memory_db)
assert s['M005_bandit_tables'] == 'failed'
```

## Next Steps


---

*Source: test_migration_runner.py:403 | Complexity: Intermediate | Last updated: 2026-05-05*