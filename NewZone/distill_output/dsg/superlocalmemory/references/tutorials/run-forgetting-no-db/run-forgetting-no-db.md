# How To: Run Forgetting No Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: POST /forgetting/run with no DB returns error gracefully.

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'POST /forgetting/run with no DB returns error gracefully.'

```python
'POST /forgetting/run with no DB returns error gracefully.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign fake_db = value

```python
fake_db = tmp_path / 'nonexistent.db'
```

**Verification:**
```python
assert data['success'] is False
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

### Step 4: Assign resp = client.post(...)

```python
resp = client.post('/api/v3/forgetting/run', json={})
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert data['success'] is False
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'POST /forgetting/run with no DB returns error gracefully.'
fake_db = tmp_path / 'nonexistent.db'
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', fake_db), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.post('/api/v3/forgetting/run', json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] is False
```

## Next Steps


---

*Source: test_api_v33.py:345 | Complexity: Intermediate | Last updated: 2026-05-05*