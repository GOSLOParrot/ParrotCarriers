# How To: Get Associations Filtered By Type

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/associations?type=auto_link filters correctly.

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
# Fixtures: seeded_db
```

## Step-by-Step Guide

### Step 1: 'GET /api/v3/associations?type=auto_link filters correctly.'

```python
'GET /api/v3/associations?type=auto_link filters correctly.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_db

```python
db_path, _, _, _ = seeded_db
```

**Verification:**
```python
assert edge['association_type'] == 'auto_link'
```

### Step 3: Assign app = _make_app_with_db(...)

```python
app = _make_app_with_db(db_path)
```

### Step 4: Assign client = TestClient(...)

```python
client = TestClient(app)
```

### Step 5: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/associations?type=auto_link&profile=default')
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 6: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert edge['association_type'] == 'auto_link'
```


## Complete Example

```python
# Setup
# Fixtures: seeded_db

# Workflow
'GET /api/v3/associations?type=auto_link filters correctly.'
db_path, _, _, _ = seeded_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    app = _make_app_with_db(db_path)
    client = TestClient(app)
    resp = client.get('/api/v3/associations?type=auto_link&profile=default')
    assert resp.status_code == 200
    data = resp.json()
    for edge in data['edges']:
        assert edge['association_type'] == 'auto_link'
```

## Next Steps


---

*Source: test_api_associations.py:76 | Complexity: Intermediate | Last updated: 2026-05-05*