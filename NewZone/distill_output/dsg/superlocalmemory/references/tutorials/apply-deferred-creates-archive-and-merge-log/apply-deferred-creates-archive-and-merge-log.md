# How To: Apply Deferred Creates Archive And Merge Log

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Deferred apply against a memory.db that includes atomic_facts.

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Deferred apply against a memory.db that includes atomic_facts.'

```python
'Deferred apply against a memory.db that includes atomic_facts.'
```

**Verification:**
```python
assert 'M011_archive_and_merge' in stats['applied']
```

### Step 2: Assign learning_db = value

```python
learning_db = tmp_path / 'learning.db'
```

**Verification:**
```python
assert {'memory_archive', 'memory_merge_log'} <= tables
```

### Step 3: Assign memory_db = value

```python
memory_db = tmp_path / 'memory.db'
```

### Step 4: Call sqlite3.connect.close()

```python
sqlite3.connect(learning_db).close()
```

### Step 5: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

### Step 6: Assign stats = mr.apply_deferred(...)

```python
stats = mr.apply_deferred(learning_db, memory_db)
```

**Verification:**
```python
assert 'M011_archive_and_merge' in stats['applied']
```

### Step 7: Assign tables = _table_names(...)

```python
tables = _table_names(memory_db)
```

**Verification:**
```python
assert {'memory_archive', 'memory_merge_log'} <= tables
```

### Step 8: Call conn.executescript()

```python
conn.executescript("\n            CREATE TABLE atomic_facts (\n                fact_id TEXT PRIMARY KEY,\n                profile_id TEXT NOT NULL DEFAULT 'default',\n                content TEXT NOT NULL DEFAULT ''\n            );\n            ")
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Deferred apply against a memory.db that includes atomic_facts.'
learning_db = tmp_path / 'learning.db'
memory_db = tmp_path / 'memory.db'
sqlite3.connect(learning_db).close()
with sqlite3.connect(memory_db) as conn:
    conn.executescript("\n            CREATE TABLE atomic_facts (\n                fact_id TEXT PRIMARY KEY,\n                profile_id TEXT NOT NULL DEFAULT 'default',\n                content TEXT NOT NULL DEFAULT ''\n            );\n            ")
mr.apply_all(learning_db, memory_db)
stats = mr.apply_deferred(learning_db, memory_db)
assert 'M011_archive_and_merge' in stats['applied']
tables = _table_names(memory_db)
assert {'memory_archive', 'memory_merge_log'} <= tables
```

## Next Steps


---

*Source: test_migration_runner.py:668 | Complexity: Advanced | Last updated: 2026-05-05*