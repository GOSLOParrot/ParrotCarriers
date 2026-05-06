# How To: Seeded Db Returns Zone Distribution

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Seeded DB returns correct zone counts.

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

### Step 1: 'Seeded DB returns correct zone counts.'

```python
'Seeded DB returns correct zone counts.'
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
assert data['total'] == 6
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert data['zones']['active'] == 2
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/forgetting/stats?profile=default')
```

**Verification:**
```python
assert data['zones']['warm'] == 1
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert data['zones']['cold'] == 1
```


## Complete Example

```python
# Setup
# Fixtures: seeded_v33_db

# Workflow
'Seeded DB returns correct zone counts.'
db_path, _, _, _ = seeded_v33_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/forgetting/stats?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == 6
    assert data['zones']['active'] == 2
    assert data['zones']['warm'] == 1
    assert data['zones']['cold'] == 1
    assert data['zones']['archive'] == 1
    assert data['zones']['forgotten'] == 1
```

## Next Steps


---

*Source: test_api_v33.py:279 | Complexity: Intermediate | Last updated: 2026-05-05*