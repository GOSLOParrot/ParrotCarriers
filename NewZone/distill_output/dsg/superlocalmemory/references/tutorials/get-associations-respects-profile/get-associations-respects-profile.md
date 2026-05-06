# How To: Get Associations Respects Profile

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/associations?profile=nonexistent returns empty (Rule 01).

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

### Step 1: 'GET /api/v3/associations?profile=nonexistent returns empty (Rule 01).'

```python
'GET /api/v3/associations?profile=nonexistent returns empty (Rule 01).'
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
assert data['edges'] == []
```

### Step 3: Assign app = _make_app_with_db(...)

```python
app = _make_app_with_db(db_path)
```

**Verification:**
```python
assert data['total'] == 0
```

### Step 4: Assign client = TestClient(...)

```python
client = TestClient(app)
```

### Step 5: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/associations?profile=nonexistent')
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
assert data['edges'] == []
```


## Complete Example

```python
# Setup
# Fixtures: seeded_db

# Workflow
'GET /api/v3/associations?profile=nonexistent returns empty (Rule 01).'
db_path, _, _, _ = seeded_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='nonexistent'):
    app = _make_app_with_db(db_path)
    client = TestClient(app)
    resp = client.get('/api/v3/associations?profile=nonexistent')
    assert resp.status_code == 200
    data = resp.json()
    assert data['edges'] == []
    assert data['total'] == 0
```

## Next Steps


---

*Source: test_api_associations.py:113 | Complexity: Intermediate | Last updated: 2026-05-05*