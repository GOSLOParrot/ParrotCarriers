# How To: Require Engine Returns Engine When Available

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: When engine is available, require_engine returns it (no exception).

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

### Step 1: 'When engine is available, require_engine returns it (no exception).'

```python
'When engine is available, require_engine returns it (no exception).'
```

**Verification:**
```python
assert engine is not None
```

### Step 2: Assign req = FakeRequest(...)

```python
req = FakeRequest()
```

**Verification:**
```python
assert require_engine(req) is engine
```

### Step 3: Assign engine = require_engine(...)

```python
engine = require_engine(req)
```

**Verification:**
```python
assert engine is not None
```

### Step 4: Assign engine = None

```python
engine = None
```

### Step 5: Assign state = FakeState(...)

```python
state = FakeState()
```

### Step 6: Assign app = FakeApp(...)

```python
app = FakeApp()
```


## Complete Example

```python
# Setup
# Fixtures: engine_db

# Workflow
'When engine is available, require_engine returns it (no exception).'
from superlocalmemory.server.routes.helpers import require_engine, get_engine_lazy

class FakeState:
    engine = None

class FakeApp:
    state = FakeState()

class FakeRequest:
    app = FakeApp()
req = FakeRequest()
engine = require_engine(req)
assert engine is not None
assert require_engine(req) is engine
```

## Next Steps


---

*Source: test_engine_lifecycle.py:254 | Complexity: Advanced | Last updated: 2026-05-05*