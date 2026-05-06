# How To: Seeded Db Returns Tier Distribution

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Seeded DB returns correct tier distribution.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `uuid`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.server.routes.v3_api`
- `fastapi`
- `superlocalmemory.storage.schema_v32`
- `superlocalmemory.storage`
- `superlocalmemory.server.routes.v3_api`
- `superlocalmemory.server.routes.v3_api`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `os`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_invoker`
- `superlocalmemory.core.config`

**Setup Required:**
```python
# Fixtures: seeded_v33_db
```

## Step-by-Step Guide

### Step 1: 'Seeded DB returns correct tier distribution.'

```python
'Seeded DB returns correct tier distribution.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_v33_db

```python
db_path, _, _, _ = seeded_v33_db
```

**Verification:**
```python
assert data['total'] == 5
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert data['tiers']['float32'] == 2
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/quantization/stats?profile=default')
```

**Verification:**
```python
assert data['tiers']['int8'] == 1
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert data['tiers']['polar4'] == 1
```


## Complete Example

```python
# Setup
# Fixtures: seeded_v33_db

# Workflow
'Seeded DB returns correct tier distribution.'
db_path, _, _, _ = seeded_v33_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/quantization/stats?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == 5
    assert data['tiers']['float32'] == 2
    assert data['tiers']['int8'] == 1
    assert data['tiers']['polar4'] == 1
    assert data['tiers']['polar2'] == 1
    assert isinstance(data['compression_ratio'], (int, float))
```

## Next Steps


---

*Source: test_api_v33.py:408 | Complexity: Intermediate | Last updated: 2026-05-05*