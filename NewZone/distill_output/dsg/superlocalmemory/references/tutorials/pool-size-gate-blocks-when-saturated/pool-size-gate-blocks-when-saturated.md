# How To: Pool Size Gate Blocks When Saturated

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test pool size gate blocks when saturated

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core.safe_fs`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign pool = _make_pool(...)

```python
pool = _make_pool(tmp_path, size=1)
```

**Verification:**
```python
assert not acquired_second.wait(timeout=0.2), 'Second acquire should block'
```

### Step 2: Assign released = threading.Event(...)

```python
released = threading.Event()
```

**Verification:**
```python
assert acquired_second.wait(timeout=1.0), 'Second never acquired after release'
```

### Step 3: Assign acquired_second = threading.Event(...)

```python
acquired_second = threading.Event()
```

### Step 4: Assign t1 = threading.Thread(...)

```python
t1 = threading.Thread(target=holder)
```

### Step 5: Call t1.start()

```python
t1.start()
```

### Step 6: Call time.sleep()

```python
time.sleep(0.05)
```

### Step 7: Assign t2 = threading.Thread(...)

```python
t2 = threading.Thread(target=latecomer)
```

### Step 8: Call t2.start()

```python
t2.start()
```

**Verification:**
```python
assert not acquired_second.wait(timeout=0.2), 'Second acquire should block'
```

### Step 9: Call released.set()

```python
released.set()
```

**Verification:**
```python
assert acquired_second.wait(timeout=1.0), 'Second never acquired after release'
```

### Step 10: Call t1.join()

```python
t1.join(timeout=1.0)
```

### Step 11: Call t2.join()

```python
t2.join(timeout=1.0)
```

### Step 12: Call pool.close()

```python
pool.close()
```

### Step 13: Call released.wait()

```python
released.wait(timeout=2.0)
```

### Step 14: Call acquired_second.set()

```python
acquired_second.set()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
pool = _make_pool(tmp_path, size=1)
released = threading.Event()
acquired_second = threading.Event()

def holder() -> None:
    with pool.acquire():
        released.wait(timeout=2.0)

def latecomer() -> None:
    with pool.acquire():
        acquired_second.set()
t1 = threading.Thread(target=holder)
t1.start()
time.sleep(0.05)
t2 = threading.Thread(target=latecomer)
t2.start()
assert not acquired_second.wait(timeout=0.2), 'Second acquire should block'
released.set()
assert acquired_second.wait(timeout=1.0), 'Second never acquired after release'
t1.join(timeout=1.0)
t2.join(timeout=1.0)
pool.close()
```

## Next Steps


---

*Source: test_db_pool.py:52 | Complexity: Advanced | Last updated: 2026-05-05*