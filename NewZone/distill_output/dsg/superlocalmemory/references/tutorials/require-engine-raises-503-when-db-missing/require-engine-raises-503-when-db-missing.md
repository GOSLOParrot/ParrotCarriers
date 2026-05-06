# How To: Require Engine Raises 503 When Db Missing

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: If the DB is genuinely missing, require_engine should raise 503.

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
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'If the DB is genuinely missing, require_engine should raise 503.'

```python
'If the DB is genuinely missing, require_engine should raise 503.'
```

**Verification:**
```python
assert exc.status_code == 503
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.core.config.DEFAULT_BASE_DIR', tmp_path / 'nonexistent')
```

### Step 3: Assign _helpers._last_engine_failure = 0.0

```python
_helpers._last_engine_failure = 0.0
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

### Step 7: Call require_engine()

```python
require_engine(FakeRequest())
```

**Verification:**
```python
assert exc.status_code == 503
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'If the DB is genuinely missing, require_engine should raise 503.'
from fastapi import HTTPException
from superlocalmemory.server.routes.helpers import require_engine
monkeypatch.setattr('superlocalmemory.core.config.DEFAULT_BASE_DIR', tmp_path / 'nonexistent')

class FakeState:
    engine = None

class FakeApp:
    state = FakeState()

class FakeRequest:
    app = FakeApp()
import superlocalmemory.server.routes.helpers as _helpers
_helpers._last_engine_failure = 0.0
try:
    require_engine(FakeRequest())
except HTTPException as exc:
    assert exc.status_code == 503
    return
```

## Next Steps


---

*Source: test_engine_lifecycle.py:225 | Complexity: Advanced | Last updated: 2026-05-05*