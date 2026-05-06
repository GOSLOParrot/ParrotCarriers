# How To: Record Batch Writes 20 Feature Names

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test record batch writes 20 feature names

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `time`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `queue`
- `superlocalmemory.learning.features`

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
assert set(parsed.keys()) == set(FEATURE_NAMES)
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

**Verification:**
```python
assert len(parsed) == 20
```

### Step 3: Assign batch = make_batch(...)

```python
batch = make_batch(n_candidates=1)
```

### Step 4: Call record_signal_batch()

```python
record_signal_batch(conn, batch)
```

### Step 5: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT features_json FROM learning_features LIMIT 1').fetchone()
```

### Step 6: Assign parsed = json.loads(...)

```python
parsed = json.loads(dict(row)['features_json'])
```

**Verification:**
```python
assert set(parsed.keys()) == set(FEATURE_NAMES)
```

### Step 7: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
from superlocalmemory.learning.features import FEATURE_NAMES
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
batch = make_batch(n_candidates=1)
record_signal_batch(conn, batch)
row = conn.execute('SELECT features_json FROM learning_features LIMIT 1').fetchone()
parsed = json.loads(dict(row)['features_json'])
assert set(parsed.keys()) == set(FEATURE_NAMES)
assert len(parsed) == 20
conn.close()
```

## Next Steps


---

*Source: test_signals_pipeline.py:304 | Complexity: Intermediate | Last updated: 2026-05-05*