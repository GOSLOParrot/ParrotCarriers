# How To: Put Core Memory Block

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: PUT /api/v3/core-memory/{block_id} updates content.

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

### Step 1: 'PUT /api/v3/core-memory/{block_id} updates content.'

```python
'PUT /api/v3/core-memory/{block_id} updates content.'
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
assert data['content'] == new_content
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert data['char_count'] == len(new_content)
```

### Step 4: Assign bid = value

```python
bid = block_ids[0]
```

**Verification:**
```python
assert data['version'] == 2
```

### Step 5: Assign new_content = 'Updated core memory content for testing'

```python
new_content = 'Updated core memory content for testing'
```

**Verification:**
```python
assert data['compiled_by'] == 'manual'
```

### Step 6: Assign resp = client.put(...)

```python
resp = client.put(f'/api/v3/core-memory/{bid}', json={'content': new_content})
```

**Verification:**
```python
assert updated['content'] == new_content
```

### Step 7: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert data['content'] == new_content
```

### Step 8: Assign resp2 = client.get(...)

```python
resp2 = client.get('/api/v3/core-memory?profile=default')
```

### Step 9: Assign blocks = value

```python
blocks = resp2.json()['blocks']
```

### Step 10: Assign updated = value

```python
updated = [b for b in blocks if b['block_id'] == bid][0]
```

**Verification:**
```python
assert updated['content'] == new_content
```


## Complete Example

```python
# Setup
# Fixtures: seeded_db

# Workflow
'PUT /api/v3/core-memory/{block_id} updates content.'
db_path, _, _, block_ids = seeded_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    bid = block_ids[0]
    new_content = 'Updated core memory content for testing'
    resp = client.put(f'/api/v3/core-memory/{bid}', json={'content': new_content})
    assert resp.status_code == 200
    data = resp.json()
    assert data['content'] == new_content
    assert data['char_count'] == len(new_content)
    assert data['version'] == 2
    assert data['compiled_by'] == 'manual'
    resp2 = client.get('/api/v3/core-memory?profile=default')
    blocks = resp2.json()['blocks']
    updated = [b for b in blocks if b['block_id'] == bid][0]
    assert updated['content'] == new_content
```

## Next Steps


---

*Source: test_api_consolidation.py:173 | Complexity: Advanced | Last updated: 2026-05-05*