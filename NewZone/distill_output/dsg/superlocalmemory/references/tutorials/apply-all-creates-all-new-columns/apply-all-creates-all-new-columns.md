# How To: Apply All Creates All New Columns

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test apply all creates all new columns

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
assert {'query_id', 'query_text_hash', 'position', 'channel_scores', 'cross_encoder'} <= sig_cols
```

### Step 2: Call mr.apply_all()

```python
mr.apply_all(learning_db, memory_db)
```

**Verification:**
```python
assert {'signal_id', 'is_synthetic'} <= feat_cols
```

### Step 3: Assign sig_cols = set(...)

```python
sig_cols = set(_table_cols(learning_db, 'learning_signals'))
```

**Verification:**
```python
assert {'model_version', 'bytes_sha256', 'is_active', 'trained_at', 'metrics_json', 'feature_names', 'trained_on_count'} <= model_cols
```

### Step 4: Assign feat_cols = set(...)

```python
feat_cols = set(_table_cols(learning_db, 'learning_features'))
```

**Verification:**
```python
assert {'signal_id', 'is_synthetic'} <= feat_cols
```

### Step 5: Assign model_cols = set(...)

```python
model_cols = set(_table_cols(learning_db, 'learning_model_state'))
```

**Verification:**
```python
assert {'model_version', 'bytes_sha256', 'is_active', 'trained_at', 'metrics_json', 'feature_names', 'trained_on_count'} <= model_cols
```


## Complete Example

```python
# Setup
# Fixtures: fresh_dbs

# Workflow
learning_db, memory_db = fresh_dbs
mr.apply_all(learning_db, memory_db)
sig_cols = set(_table_cols(learning_db, 'learning_signals'))
assert {'query_id', 'query_text_hash', 'position', 'channel_scores', 'cross_encoder'} <= sig_cols
feat_cols = set(_table_cols(learning_db, 'learning_features'))
assert {'signal_id', 'is_synthetic'} <= feat_cols
model_cols = set(_table_cols(learning_db, 'learning_model_state'))
assert {'model_version', 'bytes_sha256', 'is_active', 'trained_at', 'metrics_json', 'feature_names', 'trained_on_count'} <= model_cols
```

## Next Steps


---

*Source: test_migration_runner.py:156 | Complexity: Intermediate | Last updated: 2026-05-05*