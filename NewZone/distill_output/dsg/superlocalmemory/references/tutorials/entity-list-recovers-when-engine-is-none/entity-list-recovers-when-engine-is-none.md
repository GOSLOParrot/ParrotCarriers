# How To: Entity List Recovers When Engine Is None

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: After mode change (engine=None), /api/entity/list must lazy-init and return 200.

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

### Step 1: 'After mode change (engine=None), /api/entity/list must lazy-init and return 200.'

```python
'After mode change (engine=None), /api/entity/list must lazy-init and return 200.'
```

**Verification:**
```python
assert app.state.engine is None
```

### Step 2: Assign app = _make_app_with_entity_routes(...)

```python
app = _make_app_with_entity_routes()
```

**Verification:**
```python
assert resp.status_code == 200, f'Expected 200 after lazy init, got {resp.status_code}: {resp.text}'
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(app)
```

**Verification:**
```python
assert 'entities' in body
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/entity/list?limit=10')
```

**Verification:**
```python
assert body['total'] >= 2
```

### Step 5: Assign body = resp.json(...)

```python
body = resp.json()
```

**Verification:**
```python
assert app.state.engine is not None
```


## Complete Example

```python
# Setup
# Fixtures: engine_db

# Workflow
'After mode change (engine=None), /api/entity/list must lazy-init and return 200.'
from fastapi.testclient import TestClient
app = _make_app_with_entity_routes()
assert app.state.engine is None
client = TestClient(app)
resp = client.get('/api/entity/list?limit=10')
assert resp.status_code == 200, f'Expected 200 after lazy init, got {resp.status_code}: {resp.text}'
body = resp.json()
assert 'entities' in body
assert body['total'] >= 2
assert app.state.engine is not None
```

## Next Steps


---

*Source: test_engine_lifecycle.py:114 | Complexity: Intermediate | Last updated: 2026-05-05*