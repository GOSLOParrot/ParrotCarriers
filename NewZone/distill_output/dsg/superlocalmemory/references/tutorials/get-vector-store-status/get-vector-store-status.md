# How To: Get Vector Store Status

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: GET /api/v3/vector-store/status returns health info.

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
# Fixtures: empty_db
```

## Step-by-Step Guide

### Step 1: 'GET /api/v3/vector-store/status returns health info.'

```python
'GET /api/v3/vector-store/status returns health info.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign mock_cfg = _mock_slm_config(...)

```python
mock_cfg = _mock_slm_config()
```

**Verification:**
```python
assert 'available' in data
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert 'provider' in data
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/vector-store/status')
```

**Verification:**
```python
assert data['provider'] == 'sqlite-vec'
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert 'dimension' in data
```


## Complete Example

```python
# Setup
# Fixtures: empty_db

# Workflow
'GET /api/v3/vector-store/status returns health info.'
from fastapi.testclient import TestClient
mock_cfg = _mock_slm_config()
with patch('superlocalmemory.server.routes.helpers.DB_PATH', empty_db), patch('superlocalmemory.core.config.SLMConfig.load', return_value=mock_cfg):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/vector-store/status')
    assert resp.status_code == 200
    data = resp.json()
    assert 'available' in data
    assert 'provider' in data
    assert data['provider'] == 'sqlite-vec'
    assert 'dimension' in data
    assert isinstance(data['dimension'], int)
    assert 'embedding_model' in data
    assert 'total_vectors' in data
    assert 'binary_quantization' in data
```

## Next Steps


---

*Source: test_api_consolidation.py:232 | Complexity: Intermediate | Last updated: 2026-05-05*