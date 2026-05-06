# How To: Cache Concurrent Miss Double Load Safe

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Two threads racing on the same key: both may call loader, final value
deterministic; size == 1.

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `time`
- `dataclasses`
- `datetime`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.learning.ensemble`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.storage.migration_runner`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning`
- `superlocalmemory.learning`


## Step-by-Step Guide

### Step 1: 'Two threads racing on the same key: both may call loader, final value\n    deterministic; size == 1.'

```python
'Two threads racing on the same key: both may call loader, final value\n    deterministic; size == 1.'
```

**Verification:**
```python
assert cache.size() == 1
```

### Step 2: Assign cache = _BanditCache(...)

```python
cache = _BanditCache(max_entries=4)
```

**Verification:**
```python
assert all((r == {'a': (1.0, 1.0)} for r in results))
```

### Step 3: Assign loads = value

```python
loads = {'n': 0}
```

### Step 4: Assign lock = threading.Lock(...)

```python
lock = threading.Lock()
```

### Step 5: Assign results = value

```python
results = []
```

### Step 6: Assign ts = value

```python
ts = [threading.Thread(target=_worker) for _ in range(4)]
```

**Verification:**
```python
assert cache.size() == 1
```

### Step 7: Call time.sleep()

```python
time.sleep(0.01)
```

### Step 8: Call results.append()

```python
results.append(cache.get('p', 's', _loader))
```

### Step 9: Call t.start()

```python
t.start()
```

### Step 10: Call t.join()

```python
t.join()
```


## Complete Example

```python
# Workflow
'Two threads racing on the same key: both may call loader, final value\n    deterministic; size == 1.'
cache = _BanditCache(max_entries=4)
loads = {'n': 0}
lock = threading.Lock()

def _loader(p, s):
    with lock:
        loads['n'] += 1
    time.sleep(0.01)
    return {'a': (1.0, 1.0)}
results = []

def _worker():
    results.append(cache.get('p', 's', _loader))
ts = [threading.Thread(target=_worker) for _ in range(4)]
for t in ts:
    t.start()
for t in ts:
    t.join()
assert cache.size() == 1
assert all((r == {'a': (1.0, 1.0)} for r in results))
```

## Next Steps


---

*Source: test_bandit_supplementary.py:98 | Complexity: Advanced | Last updated: 2026-05-05*