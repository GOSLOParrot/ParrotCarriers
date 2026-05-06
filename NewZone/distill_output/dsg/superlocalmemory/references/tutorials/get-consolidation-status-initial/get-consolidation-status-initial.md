# How To: Get Consolidation Status Initial

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Returns config flags even when no consolidation has run.

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

### Step 1: 'Returns config flags even when no consolidation has run.'

```python
'Returns config flags even when no consolidation has run.'
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
assert 'enabled' in data
```

### Step 3: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert 'triggers' in data
```

### Step 4: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/consolidation/status?profile=default')
```

**Verification:**
```python
assert 'session_end' in data['triggers']
```

### Step 5: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert 'idle_timeout' in data['triggers']
```


## Complete Example

```python
# Setup
# Fixtures: empty_db

# Workflow
'Returns config flags even when no consolidation has run.'
from fastapi.testclient import TestClient
mock_cfg = _mock_slm_config()
with patch('superlocalmemory.server.routes.helpers.DB_PATH', empty_db), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'), patch('superlocalmemory.core.config.SLMConfig.load', return_value=mock_cfg):
    client = TestClient(_make_app())
    resp = client.get('/api/v3/consolidation/status?profile=default')
    assert resp.status_code == 200
    data = resp.json()
    assert 'enabled' in data
    assert 'triggers' in data
    assert 'session_end' in data['triggers']
    assert 'idle_timeout' in data['triggers']
    assert 'step_count' in data['triggers']
    assert 'store_count_since_last' in data
```

## Next Steps


---

*Source: test_api_consolidation.py:50 | Complexity: Intermediate | Last updated: 2026-05-05*