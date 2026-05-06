# How To: Seeded Db Returns Blocks

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Seeded DB returns CCQ blocks with metadata.

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

### Step 1: 'Seeded DB returns CCQ blocks with metadata.'

```python
'Seeded DB returns CCQ blocks with metadata.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_v33_db

```python
db_path, _, block_ids, _ = seeded_v33_db
```

**Verification:**
```python
assert data['total'] == len(block_ids)
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert len(data['blocks']) == len(block_ids)
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/ccq/blocks?profile=default')
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
assert 'content' in block
```

### Step 6: Assign block = value

```python
block = data['blocks'][0]
```

**Verification:**
```python
assert 'source_fact_count' in block
```


## Complete Example

```python
# Setup
# Fixtures: seeded_v33_db

# Workflow
'Seeded DB returns CCQ blocks with metadata.'
db_path, _, block_ids, _ = seeded_v33_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/ccq/blocks?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == len(block_ids)
    assert len(data['blocks']) == len(block_ids)
    block = data['blocks'][0]
    assert 'block_id' in block
    assert 'content' in block
    assert 'source_fact_count' in block
    assert 'cluster_id' in block
    assert block['source_fact_count'] >= 2
```

## Next Steps


---

*Source: test_api_v33.py:448 | Complexity: Intermediate | Last updated: 2026-05-05*