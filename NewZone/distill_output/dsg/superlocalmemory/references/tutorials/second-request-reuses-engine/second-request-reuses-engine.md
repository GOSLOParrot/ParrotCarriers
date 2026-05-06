# How To: Second Request Reuses Engine

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Two consecutive requests share the same engine instance (no re-init).

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

### Step 1: 'Two consecutive requests share the same engine instance (no re-init).'

```python
'Two consecutive requests share the same engine instance (no re-init).'
```

**Verification:**
```python
assert resp1.status_code == 200
```

### Step 2: Assign app = _make_app_with_entity_routes(...)

```python
app = _make_app_with_entity_routes()
```

**Verification:**
```python
assert engine_after_first is not None
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(app)
```

**Verification:**
```python
assert resp2.status_code == 200
```

### Step 4: Assign resp1 = client.get(...)

```python
resp1 = client.get('/api/entity/list?limit=10')
```

**Verification:**
```python
assert app.state.engine is engine_after_first
```

### Step 5: Assign engine_after_first = value

```python
engine_after_first = app.state.engine
```

**Verification:**
```python
assert engine_after_first is not None
```

### Step 6: Assign resp2 = client.get(...)

```python
resp2 = client.get('/api/entity/list?limit=10')
```

**Verification:**
```python
assert resp2.status_code == 200
```


## Complete Example

```python
# Setup
# Fixtures: engine_db

# Workflow
'Two consecutive requests share the same engine instance (no re-init).'
from fastapi.testclient import TestClient
app = _make_app_with_entity_routes()
client = TestClient(app)
resp1 = client.get('/api/entity/list?limit=10')
assert resp1.status_code == 200
engine_after_first = app.state.engine
assert engine_after_first is not None
resp2 = client.get('/api/entity/list?limit=10')
assert resp2.status_code == 200
assert app.state.engine is engine_after_first
```

## Next Steps


---

*Source: test_engine_lifecycle.py:133 | Complexity: Intermediate | Last updated: 2026-05-05*