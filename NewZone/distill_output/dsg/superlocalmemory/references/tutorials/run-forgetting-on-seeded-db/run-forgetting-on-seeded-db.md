# How To: Run Forgetting On Seeded Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: POST /forgetting/run decays retention scores.

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

### Step 1: 'POST /forgetting/run decays retention scores.'

```python
'POST /forgetting/run decays retention scores.'
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
assert data['success'] is True
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert 'facts_decayed' in data
```

### Step 4: Assign resp = client.post(...)

```python
resp = client.post('/api/v3/forgetting/run', json={'profile': 'default'})
```

**Verification:**
```python
assert data['profile'] == 'default'
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert data['success'] is True
```


## Complete Example

```python
# Setup
# Fixtures: seeded_v33_db

# Workflow
'POST /forgetting/run decays retention scores.'
db_path, _, _, _ = seeded_v33_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.post('/api/v3/forgetting/run', json={'profile': 'default'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] is True
    assert 'facts_decayed' in data
    assert data['profile'] == 'default'
```

## Next Steps


---

*Source: test_api_v33.py:330 | Complexity: Intermediate | Last updated: 2026-05-05*