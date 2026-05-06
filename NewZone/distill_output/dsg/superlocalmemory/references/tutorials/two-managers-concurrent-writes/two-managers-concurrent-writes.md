# How To: Two Managers Concurrent Writes

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Two DatabaseManager instances (simulating two processes) writing.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `threading`
- `time`
- `pathlib`
- `concurrent.futures`
- `pytest`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Two DatabaseManager instances (simulating two processes) writing.'

```python
'Two DatabaseManager instances (simulating two processes) writing.'
```

**Verification:**
```python
assert not errors, f'Errors: {errors}'
```

### Step 2: Assign db_path = value

```python
db_path = tmp_path / 'shared.db'
```

**Verification:**
```python
assert db1.get_fact_count('default') == 10
```

### Step 3: Assign db1 = DatabaseManager(...)

```python
db1 = DatabaseManager(db_path)
```

### Step 4: Call db1.initialize()

```python
db1.initialize(schema)
```

### Step 5: Assign db2 = DatabaseManager(...)

```python
db2 = DatabaseManager(db_path)
```

### Step 6: Assign t1 = threading.Thread(...)

```python
t1 = threading.Thread(target=_write_from_db, args=(db1, 0))
```

### Step 7: Assign t2 = threading.Thread(...)

```python
t2 = threading.Thread(target=_write_from_db, args=(db2, 100))
```

### Step 8: Call t1.start()

```python
t1.start()
```

### Step 9: Call t2.start()

```python
t2.start()
```

### Step 10: Call t1.join()

```python
t1.join(timeout=30)
```

### Step 11: Call t2.join()

```python
t2.join(timeout=30)
```

**Verification:**
```python
assert not errors, f'Errors: {errors}'
```

### Step 12: Call _store_fact_with_parent()

```python
_store_fact_with_parent(db, n=start + i)
```

### Step 13: Call errors.append()

```python
errors.append(exc)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Two DatabaseManager instances (simulating two processes) writing.'
db_path = tmp_path / 'shared.db'
db1 = DatabaseManager(db_path)
db1.initialize(schema)
db2 = DatabaseManager(db_path)
errors: list[Exception] = []

def _write_from_db(db: DatabaseManager, start: int) -> None:
    try:
        for i in range(5):
            _store_fact_with_parent(db, n=start + i)
    except Exception as exc:
        errors.append(exc)
t1 = threading.Thread(target=_write_from_db, args=(db1, 0))
t2 = threading.Thread(target=_write_from_db, args=(db2, 100))
t1.start()
t2.start()
t1.join(timeout=30)
t2.join(timeout=30)
assert not errors, f'Errors: {errors}'
assert db1.get_fact_count('default') == 10
```

## Next Steps


---

*Source: test_concurrent_db.py:213 | Complexity: Advanced | Last updated: 2026-05-05*