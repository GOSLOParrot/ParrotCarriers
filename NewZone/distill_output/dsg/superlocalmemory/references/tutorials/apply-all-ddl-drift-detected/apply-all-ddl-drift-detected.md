# How To: Apply All Ddl Drift Detected

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test apply all ddl drift detected

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
assert 'drift' in m1_detail.lower()
```

### Step 2: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

### Step 3: Assign stats = mr.apply_all(...)

```python
stats = mr.apply_all(learning_db, memory_db)
```

### Step 4: Assign details = stats.get(...)

```python
details = stats.get('details', {})
```

### Step 5: Assign m1_detail = details.get(...)

```python
m1_detail = details.get('M001_add_signal_features_columns', '')
```

**Verification:**
```python
assert 'drift' in m1_detail.lower()
```

### Step 6: Call conn.execute()

```python
conn.execute("UPDATE migration_log SET ddl_sha256 = 'deadbeef' WHERE name = 'M001_add_signal_features_columns'")
```

### Step 7: Call conn.commit()

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
    conn.execute("UPDATE migration_log SET ddl_sha256 = 'deadbeef' WHERE name = 'M001_add_signal_features_columns'")
    conn.commit()
stats = mr.apply_all(learning_db, memory_db)
details = stats.get('details', {})
m1_detail = details.get('M001_add_signal_features_columns', '')
assert 'drift' in m1_detail.lower()
```

## Next Steps


---

*Source: test_migration_runner.py:263 | Complexity: Intermediate | Last updated: 2026-05-05*