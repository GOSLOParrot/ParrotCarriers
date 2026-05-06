# How To: Apply Deferred Adds Reward Column

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: apply_deferred wires the M006 reward column onto action_outcomes.

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

### Step 1: 'apply_deferred wires the M006 reward column onto action_outcomes.'

```python
'apply_deferred wires the M006 reward column onto action_outcomes.'
```

**Verification:**
```python
assert 'M006_action_outcomes_reward' in stats['applied']
```

### Step 2: Assign unknown = fresh_dbs

```python
learning_db, memory_db = fresh_dbs
```

**Verification:**
```python
assert stats['failed'] == []
```

### Step 3: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

**Verification:**
```python
assert 'reward' in cols
```

### Step 4: Assign stats = mr.apply_deferred(...)

```python
stats = mr.apply_deferred(learning_db, memory_db)
```

**Verification:**
```python
assert 'idx_action_outcomes_settled_reward' in idx
```

### Step 5: Assign cols = _table_cols(...)

```python
cols = _table_cols(memory_db, 'action_outcomes')
```

**Verification:**
```python
assert 'reward' in cols
```

### Step 6: Assign idx = value

```python
idx = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
'apply_deferred wires the M006 reward column onto action_outcomes.'
learning_db, memory_db = fresh_dbs
mr.apply_all(learning_db, memory_db)
stats = mr.apply_deferred(learning_db, memory_db)
assert 'M006_action_outcomes_reward' in stats['applied']
assert stats['failed'] == []
cols = _table_cols(memory_db, 'action_outcomes')
assert 'reward' in cols
with sqlite3.connect(memory_db) as conn:
    idx = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
assert 'idx_action_outcomes_settled_reward' in idx
```

## Next Steps


---

*Source: test_migration_runner.py:470 | Complexity: Intermediate | Last updated: 2026-05-05*