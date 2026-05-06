# How To: Get Associations Empty

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/associations returns empty list when no edges exist.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.server.routes.v3_api`
- `fastapi`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`

**Setup Required:**
```python
# Fixtures: empty_db
```

## Step-by-Step Guide

### Step 1: 'GET /api/v3/associations returns empty list when no edges exist.'

```python
'GET /api/v3/associations returns empty list when no edges exist.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign app = _make_app_with_db(...)

```python
app = _make_app_with_db(empty_db)
```

**Verification:**
```python
assert data['edges'] == []
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(app)
```

**Verification:**
```python
assert data['total'] == 0
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/associations?profile=default')
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
assert data['edges'] == []
```


## Complete Example

```python
# Setup
# Fixtures: empty_db

# Workflow
'GET /api/v3/associations returns empty list when no edges exist.'
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', empty_db), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    app = _make_app_with_db(empty_db)
    client = TestClient(app)
    resp = client.get('/api/v3/associations?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert data['edges'] == []
    assert data['total'] == 0
```

## Next Steps


---

*Source: test_api_associations.py:37 | Complexity: Intermediate | Last updated: 2026-05-05*