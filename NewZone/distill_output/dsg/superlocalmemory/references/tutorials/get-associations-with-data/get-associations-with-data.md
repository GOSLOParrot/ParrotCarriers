# How To: Get Associations With Data

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/associations returns edges with previews.

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

### Step 1: 'GET /api/v3/associations returns edges with previews.'

```python
'GET /api/v3/associations returns edges with previews.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_db

```python
db_path, fact_ids, edge_ids, _ = seeded_db
```

**Verification:**
```python
assert len(data['edges']) > 0
```

### Step 3: Assign app = _make_app_with_db(...)

```python
app = _make_app_with_db(db_path)
```

**Verification:**
```python
assert data['total'] == len(edge_ids)
```

### Step 4: Assign client = TestClient(...)

```python
client = TestClient(app)
```

**Verification:**
```python
assert 'edge_id' in edge
```

### Step 5: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/associations?profile=default')
```

**Verification:**
```python
assert 'source_fact_id' in edge
```

### Step 6: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert 'target_fact_id' in edge
```

### Step 7: Assign edge = value

```python
edge = data['edges'][0]
```

**Verification:**
```python
assert 'association_type' in edge
```


## Complete Example

```python
# Setup
# Fixtures: seeded_db

# Workflow
'GET /api/v3/associations returns edges with previews.'
db_path, fact_ids, edge_ids, _ = seeded_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    app = _make_app_with_db(db_path)
    client = TestClient(app)
    resp = client.get('/api/v3/associations?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['edges']) > 0
    assert data['total'] == len(edge_ids)
    edge = data['edges'][0]
    assert 'edge_id' in edge
    assert 'source_fact_id' in edge
    assert 'target_fact_id' in edge
    assert 'association_type' in edge
    assert 'weight' in edge
    assert 'source_preview' in edge
    assert 'target_preview' in edge
    assert len(edge['source_preview']) > 0
```

## Next Steps


---

*Source: test_api_associations.py:51 | Complexity: Intermediate | Last updated: 2026-05-05*