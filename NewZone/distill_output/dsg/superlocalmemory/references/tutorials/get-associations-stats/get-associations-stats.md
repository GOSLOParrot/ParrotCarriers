# How To: Get Associations Stats

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/associations/stats returns correct aggregates.

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

### Step 1: 'GET /api/v3/associations/stats returns correct aggregates.'

```python
'GET /api/v3/associations/stats returns correct aggregates.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_db

```python
db_path, _, edge_ids, _ = seeded_db
```

**Verification:**
```python
assert 'total_edges' in data
```

### Step 3: Assign app = _make_app_with_db(...)

```python
app = _make_app_with_db(db_path)
```

**Verification:**
```python
assert data['total_edges'] == len(edge_ids)
```

### Step 4: Assign client = TestClient(...)

```python
client = TestClient(app)
```

**Verification:**
```python
assert 'by_type' in data
```

### Step 5: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/associations/stats?profile=default')
```

**Verification:**
```python
assert isinstance(data['by_type'], dict)
```

### Step 6: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert 'avg_weight' in data
```


## Complete Example

```python
# Setup
# Fixtures: seeded_db

# Workflow
'GET /api/v3/associations/stats returns correct aggregates.'
db_path, _, edge_ids, _ = seeded_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    app = _make_app_with_db(db_path)
    client = TestClient(app)
    resp = client.get('/api/v3/associations/stats?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert 'total_edges' in data
    assert data['total_edges'] == len(edge_ids)
    assert 'by_type' in data
    assert isinstance(data['by_type'], dict)
    assert 'avg_weight' in data
    assert isinstance(data['avg_weight'], float)
    assert 'community_count' in data
    assert 'top_connected_facts' in data
```

## Next Steps


---

*Source: test_api_associations.py:91 | Complexity: Intermediate | Last updated: 2026-05-05*