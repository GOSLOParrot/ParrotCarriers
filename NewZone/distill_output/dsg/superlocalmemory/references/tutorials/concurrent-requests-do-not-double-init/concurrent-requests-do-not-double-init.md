# How To: Concurrent Requests Do Not Double Init

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Under concurrent load, only ONE engine should be created.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `threading`
- `uuid`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.storage.schema_v32`
- `superlocalmemory.storage`
- `superlocalmemory.server.routes.helpers`
- `fastapi`
- `superlocalmemory.server.routes.entity`
- `fastapi.testclient`
- `fastapi.testclient`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes`
- `superlocalmemory.core.engine`
- `fastapi`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes`

**Setup Required:**
```python
# Fixtures: engine_db
```

## Step-by-Step Guide

### Step 1: 'Under concurrent load, only ONE engine should be created.'

```python
'Under concurrent load, only ONE engine should be created.'
```

**Verification:**
```python
assert not errors, f'Worker errors: {errors}'
```

### Step 2: Assign state = FakeState(...)

```python
state = FakeState()
```

**Verification:**
```python
assert len(unique_engines) == 1, f'Expected one engine under contention, got {len(unique_engines)}'
```

### Step 3: Assign threads = value

```python
threads = [threading.Thread(target=worker) for _ in range(8)]
```

**Verification:**
```python
assert not errors, f'Worker errors: {errors}'
```

### Step 4: Assign unique_engines = value

```python
unique_engines = {id(e) for e in results if e is not None}
```

**Verification:**
```python
assert len(unique_engines) == 1, f'Expected one engine under contention, got {len(unique_engines)}'
```

### Step 5: Call t.start()

```python
t.start()
```

### Step 6: Call t.join()

```python
t.join(timeout=30)
```

### Step 7: Assign self.engine = None

```python
self.engine = None
```

### Step 8: Call results.append()

```python
results.append(get_engine_lazy(state))
```

### Step 9: Call errors.append()

```python
errors.append(exc)
```


## Complete Example

```python
# Setup
# Fixtures: engine_db

# Workflow
'Under concurrent load, only ONE engine should be created.'
from superlocalmemory.server.routes.helpers import get_engine_lazy

class FakeState:

    def __init__(self):
        self.engine = None
state = FakeState()
results: list[object] = []
errors: list[Exception] = []

def worker():
    try:
        results.append(get_engine_lazy(state))
    except Exception as exc:
        errors.append(exc)
threads = [threading.Thread(target=worker) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=30)
assert not errors, f'Worker errors: {errors}'
unique_engines = {id(e) for e in results if e is not None}
assert len(unique_engines) == 1, f'Expected one engine under contention, got {len(unique_engines)}'
```

## Next Steps


---

*Source: test_engine_lifecycle.py:149 | Complexity: Advanced | Last updated: 2026-05-05*