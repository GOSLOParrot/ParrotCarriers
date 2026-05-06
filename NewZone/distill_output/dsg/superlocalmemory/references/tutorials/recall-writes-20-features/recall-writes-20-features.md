# How To: Recall Writes 20 Features

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test recall writes 20 features

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `re`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(tmp_path)
```

**Verification:**
```python
assert len(rows) == 5
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

**Verification:**
```python
assert len(parsed) == FEATURE_DIM == 20
```

### Step 3: Call record_signal_batch()

```python
record_signal_batch(conn, make_batch(n_candidates=5))
```

### Step 4: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT features_json FROM learning_features').fetchall()
```

**Verification:**
```python
assert len(rows) == 5
```

### Step 5: Call conn.close()

```python
conn.close()
```

### Step 6: Assign parsed = json.loads(...)

```python
parsed = json.loads(dict(r)['features_json'])
```

**Verification:**
```python
assert len(parsed) == FEATURE_DIM == 20
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
record_signal_batch(conn, make_batch(n_candidates=5))
rows = conn.execute('SELECT features_json FROM learning_features').fetchall()
assert len(rows) == 5
for r in rows:
    parsed = json.loads(dict(r)['features_json'])
    assert len(parsed) == FEATURE_DIM == 20
conn.close()
```

## Next Steps


---

*Source: test_feature_extraction_wired.py:35 | Complexity: Intermediate | Last updated: 2026-05-05*