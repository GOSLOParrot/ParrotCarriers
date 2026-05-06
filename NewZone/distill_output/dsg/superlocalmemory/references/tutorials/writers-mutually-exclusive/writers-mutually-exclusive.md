# How To: Writers Mutually Exclusive

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test writers mutually exclusive

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
assert counter['peak'] == 1, f"Peak concurrent writers: {counter['peak']}"
```

### Step 2: Assign lock = EngineRWLock(...)

```python
lock = EngineRWLock()
```

### Step 3: Assign counter = value

```python
counter = {'active': 0, 'peak': 0}
```

### Step 4: Assign counter_lock = threading.Lock(...)

```python
counter_lock = threading.Lock()
```

### Step 5: Assign iterations = 50

```python
iterations = 50
```

### Step 6: Assign threads = value

```python
threads = [threading.Thread(target=writer) for _ in range(4)]
```

**Verification:**
```python
assert counter['peak'] == 1, f"Peak concurrent writers: {counter['peak']}"
```

### Step 7: Call t.start()

```python
t.start()
```

### Step 8: Call t.join()

```python
t.join(timeout=5.0)
```

### Step 9: Call time.sleep()

```python
time.sleep(0.001)
```

### Step 10: Assign unknown = value

```python
counter['peak'] = counter['active']
```


## Complete Example

```python
# Workflow
EngineRWLock = _import_lock()
lock = EngineRWLock()
counter = {'active': 0, 'peak': 0}
counter_lock = threading.Lock()
iterations = 50

def writer() -> None:
    for _ in range(iterations):
        with lock.write():
            with counter_lock:
                counter['active'] += 1
                if counter['active'] > counter['peak']:
                    counter['peak'] = counter['active']
            time.sleep(0.001)
            with counter_lock:
                counter['active'] -= 1
threads = [threading.Thread(target=writer) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=5.0)
assert counter['peak'] == 1, f"Peak concurrent writers: {counter['peak']}"
```

## Next Steps


---

*Source: test_engine_lock.py:105 | Complexity: Advanced | Last updated: 2026-05-05*