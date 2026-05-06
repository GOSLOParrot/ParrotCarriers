# How To: Exception Releases Reader

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test exception releases reader

## Prerequisites

**Required Modules:**
- `__future__`
- `threading`
- `time`
- `pytest`
- `superlocalmemory.core.engine_lock`


## Step-by-Step Guide

### Step 1: Assign EngineRWLock = _import_lock(...)

```python
EngineRWLock = _import_lock()
```

**Verification:**
```python
assert acquired.wait(timeout=1.0), 'Lock leaked after reader exception'
```

### Step 2: Assign lock = EngineRWLock(...)

```python
lock = EngineRWLock()
```

### Step 3: Assign acquired = threading.Event(...)

```python
acquired = threading.Event()
```

### Step 4: Assign t = threading.Thread(...)

```python
t = threading.Thread(target=writer)
```

### Step 5: Call t.start()

```python
t.start()
```

**Verification:**
```python
assert acquired.wait(timeout=1.0), 'Lock leaked after reader exception'
```

### Step 6: Call t.join()

```python
t.join(timeout=1.0)
```

### Step 7: Call acquired.set()

```python
acquired.set()
```


## Complete Example

```python
# Workflow
EngineRWLock = _import_lock()
lock = EngineRWLock()
with pytest.raises(RuntimeError, match='boom'):
    with lock.read():
        raise RuntimeError('boom')
acquired = threading.Event()

def writer() -> None:
    with lock.write():
        acquired.set()
t = threading.Thread(target=writer)
t.start()
assert acquired.wait(timeout=1.0), 'Lock leaked after reader exception'
t.join(timeout=1.0)
```

## Next Steps


---

*Source: test_engine_lock.py:168 | Complexity: Advanced | Last updated: 2026-05-05*