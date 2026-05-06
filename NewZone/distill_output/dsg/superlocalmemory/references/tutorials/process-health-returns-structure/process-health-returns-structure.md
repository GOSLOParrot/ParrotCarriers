# How To: Process Health Returns Structure

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Response has expected keys: processes, memory_mb, healthy.

## Prerequisites

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


## Step-by-Step Guide

### Step 1: 'Response has expected keys: processes, memory_mb, healthy.'

```python
'Response has expected keys: processes, memory_mb, healthy.'
```

**Verification:**
```python
assert resp.status_code == 200
```

### Step 2: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

**Verification:**
```python
assert 'processes' in data
```

### Step 3: Assign resp = client.get(...)

```python
resp = client.get('/api/v3/health/processes')
```

**Verification:**
```python
assert 'mcp_server' in data['processes']
```

### Step 4: Assign data = resp.json(...)

```python
data = resp.json()
```

**Verification:**
```python
assert data['processes']['mcp_server']['status'] == 'running'
```


## Complete Example

```python
# Workflow
'Response has expected keys: processes, memory_mb, healthy.'
from fastapi.testclient import TestClient
client = TestClient(_make_app())
resp = client.get('/api/v3/health/processes')
assert resp.status_code == 200
data = resp.json()
assert 'processes' in data
assert 'mcp_server' in data['processes']
assert data['processes']['mcp_server']['status'] == 'running'
assert 'parent' in data['processes']
assert 'memory_mb' in data
assert 'healthy' in data
```

## Next Steps


---

*Source: test_api_v33.py:537 | Complexity: Intermediate | Last updated: 2026-05-05*