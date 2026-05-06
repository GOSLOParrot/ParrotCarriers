# How To: Bandit Plays Retention Sweep

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: B8: delete 500 settled+old, keep 100 settled+new + 50 unsettled.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `datetime`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.storage.migration_runner`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: 'B8: delete 500 settled+old, keep 100 settled+new + 50 unsettled.'

```python
'B8: delete 500 settled+old, keep 100 settled+new + 50 unsettled.'
```

**Verification:**
```python
assert _count(db) == 650
```

### Step 2: Assign now = datetime(...)

```python
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
```

**Verification:**
```python
assert deleted == 500
```

### Step 3: Assign old_settled = unknown.isoformat(...)

```python
old_settled = (now - timedelta(days=10)).isoformat(timespec='seconds')
```

**Verification:**
```python
assert _count(db) == 150
```

### Step 4: Assign new_settled = unknown.isoformat(...)

```python
new_settled = (now - timedelta(days=1)).isoformat(timespec='seconds')
```

**Verification:**
```python
assert _count_unsettled(db) == 50
```

### Step 5: Assign played = unknown.isoformat(...)

```python
played = (now - timedelta(hours=1)).isoformat(timespec='seconds')
```

### Step 6: Call _seed()

```python
_seed(db, rows)
```

**Verification:**
```python
assert _count(db) == 650
```

### Step 7: Assign deleted = retention_sweep(...)

```python
deleted = retention_sweep(db, retention_days=7, now=now)
```

**Verification:**
```python
assert deleted == 500
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
'B8: delete 500 settled+old, keep 100 settled+new + 50 unsettled.'
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
old_settled = (now - timedelta(days=10)).isoformat(timespec='seconds')
new_settled = (now - timedelta(days=1)).isoformat(timespec='seconds')
played = (now - timedelta(hours=1)).isoformat(timespec='seconds')
rows: list[tuple[str, str | None]] = []
rows += [(played, old_settled)] * 500
rows += [(played, new_settled)] * 100
rows += [(played, None)] * 50
_seed(db, rows)
assert _count(db) == 650
deleted = retention_sweep(db, retention_days=7, now=now)
assert deleted == 500
assert _count(db) == 150
assert _count_unsettled(db) == 50
```

## Next Steps


---

*Source: test_retention_sweep.py:72 | Complexity: Intermediate | Last updated: 2026-05-05*