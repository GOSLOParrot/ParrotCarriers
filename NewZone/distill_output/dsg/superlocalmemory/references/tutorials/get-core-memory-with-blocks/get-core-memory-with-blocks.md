# How To: Get Core Memory With Blocks

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/core-memory returns populated blocks.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `unittest.mock`
- `pytest`
- `superlocalmemory.server.routes.v3_api`
- `fastapi`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
- `fastapi.testclient`
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

### Step 1: 'GET /api/v3/core-memory returns populated blocks.'

```python
'GET /api/v3/core-memory returns populated blocks.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_db

```python
db_path, _, _, block_ids = seeded_db
```

**Verification:**
```python
assert len(data['blocks']) == len(block_ids)
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert data['total_chars'] > 0
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/core-memory?profile=default')
```

**Verification:**
```python
assert 'block_id' in block
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert 'block_type' in block
```

### Step 6: Assign block = value

```python
block = data['blocks'][0]
```

**Verification:**
```python
assert 'content' in block
```


## Complete Example

```python
# Setup
# Fixtures: seeded_db

# Workflow
'GET /api/v3/core-memory returns populated blocks.'
db_path, _, _, block_ids = seeded_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/core-memory?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['blocks']) == len(block_ids)
    assert data['total_chars'] > 0
    block = data['blocks'][0]
    assert 'block_id' in block
    assert 'block_type' in block
    assert 'content' in block
    assert 'char_count' in block
    assert 'version' in block
    assert 'compiled_by' in block
```

## Next Steps


---

*Source: test_api_consolidation.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*