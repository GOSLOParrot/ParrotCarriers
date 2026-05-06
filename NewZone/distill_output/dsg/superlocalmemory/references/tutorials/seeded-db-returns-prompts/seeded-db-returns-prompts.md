# How To: Seeded Db Returns Prompts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Seeded DB returns active soft prompts sorted by confidence.

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

### Step 1: 'Seeded DB returns active soft prompts sorted by confidence.'

```python
'Seeded DB returns active soft prompts sorted by confidence.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign unknown = seeded_v33_db

```python
db_path, _, _, prompt_ids = seeded_v33_db
```

**Verification:**
```python
assert data['total'] == len(prompt_ids)
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert data['total_tokens'] == 35
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/soft-prompts?profile=default')
```

**Verification:**
```python
assert 'prompt_id' in prompt
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert 'category' in prompt
```

### Step 6: Assign prompt = value

```python
prompt = data['prompts'][0]
```

**Verification:**
```python
assert 'confidence' in prompt
```


## Complete Example

```python
# Setup
# Fixtures: seeded_v33_db

# Workflow
'Seeded DB returns active soft prompts sorted by confidence.'
db_path, _, _, prompt_ids = seeded_v33_db
from fastapi.testclient import TestClient
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/soft-prompts?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == len(prompt_ids)
    assert data['total_tokens'] == 35
    prompt = data['prompts'][0]
    assert 'prompt_id' in prompt
    assert 'category' in prompt
    assert 'confidence' in prompt
    assert 'token_count' in prompt
    assert data['prompts'][0]['confidence'] >= data['prompts'][1]['confidence']
```

## Next Steps


---

*Source: test_api_v33.py:506 | Complexity: Intermediate | Last updated: 2026-05-05*