# How To: Second Process Cannot Acquire

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test second process cannot acquire

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `multiprocessing`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign fl = _imports(...)

```python
fl = _imports()
```

**Verification:**
```python
assert p.exitcode == 0
```

### Step 2: Assign lock_file = value

```python
lock_file = tmp_path / 'd.lock'
```

**Verification:**
```python
assert result == 'held', f"Expected 'held', got {result}"
```

### Step 3: Assign ctx = multiprocessing.get_context(...)

```python
ctx = multiprocessing.get_context('spawn')
```

**Verification:**
```python
assert result == 'held', f"Expected 'held', got {result}"
```

### Step 4: Assign p = ctx.Process(...)

```python
p = ctx.Process(target=_child_tries_lock, args=(str(lock_file), q))
```

### Step 5: Call p.start()

```python
p.start()
```

### Step 6: Call p.join()

```python
p.join(timeout=5.0)
```

**Verification:**
```python
assert p.exitcode == 0
```

### Step 7: Assign result = q.get(...)

```python
result = q.get(timeout=1.0)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
fl = _imports()
lock_file = tmp_path / 'd.lock'
ctx = multiprocessing.get_context('spawn')
with fl.exclusive_lock(lock_file):
    q: multiprocessing.Queue = ctx.Queue()
    p = ctx.Process(target=_child_tries_lock, args=(str(lock_file), q))
    p.start()
    p.join(timeout=5.0)
    assert p.exitcode == 0
    result = q.get(timeout=1.0)
assert result == 'held', f"Expected 'held', got {result}"
```

## Next Steps


---

*Source: test_file_lock.py:51 | Complexity: Intermediate | Last updated: 2026-05-05*