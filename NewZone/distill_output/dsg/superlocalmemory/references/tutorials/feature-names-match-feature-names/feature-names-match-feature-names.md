# How To: Feature Names Match Feature Names

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test feature names match FEATURE NAMES

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
assert set(parsed.keys()) == set(FEATURE_NAMES)
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

### Step 3: Call record_signal_batch()

```python
record_signal_batch(conn, make_batch(n_candidates=1))
```

### Step 4: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT features_json FROM learning_features LIMIT 1').fetchone()
```

### Step 5: Assign parsed = json.loads(...)

```python
parsed = json.loads(dict(row)['features_json'])
```

**Verification:**
```python
assert set(parsed.keys()) == set(FEATURE_NAMES)
```

### Step 6: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
record_signal_batch(conn, make_batch(n_candidates=1))
row = conn.execute('SELECT features_json FROM learning_features LIMIT 1').fetchone()
parsed = json.loads(dict(row)['features_json'])
assert set(parsed.keys()) == set(FEATURE_NAMES)
conn.close()
```

## Next Steps


---

*Source: test_feature_extraction_wired.py:49 | Complexity: Intermediate | Last updated: 2026-05-05*