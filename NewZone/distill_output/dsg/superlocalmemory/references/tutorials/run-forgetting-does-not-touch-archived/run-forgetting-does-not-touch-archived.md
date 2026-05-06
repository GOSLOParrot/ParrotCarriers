# How To: Run Forgetting Does Not Touch Archived

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Archived/forgotten facts are NOT decayed further.

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

### Step 1: 'Archived/forgotten facts are NOT decayed further.'

```python
'Archived/forgotten facts are NOT decayed further.'
```

**Verification:**
```python
assert post_score == pre_score
```

### Step 2: Assign unknown = seeded_v33_db

```python
db_path, fact_ids, _, _ = seeded_v33_db
```

### Step 3: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 4: Assign pre_score = value

```python
pre_score = conn.execute("SELECT retention_score FROM fact_retention WHERE lifecycle_zone = 'archive' AND profile_id = 'default'").fetchone()[0]
```

### Step 5: Call conn.close()

```python
conn.close()
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 7: Assign post_score = value

```python
post_score = conn.execute("SELECT retention_score FROM fact_retention WHERE lifecycle_zone = 'archive' AND profile_id = 'default'").fetchone()[0]
```

### Step 8: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert post_score == pre_score
```

### Step 9: Assign client = TestClient(...)

```python
client = TestClient(_make_app())
```

### Step 10: Call client.post()

```python
client.post('/api/v3/forgetting/run', json={})
```


## Complete Example

```python
# Setup
# Fixtures: seeded_v33_db

# Workflow
'Archived/forgotten facts are NOT decayed further.'
db_path, fact_ids, _, _ = seeded_v33_db
from fastapi.testclient import TestClient
conn = sqlite3.connect(str(db_path))
pre_score = conn.execute("SELECT retention_score FROM fact_retention WHERE lifecycle_zone = 'archive' AND profile_id = 'default'").fetchone()[0]
conn.close()
with patch('superlocalmemory.server.routes.helpers.DB_PATH', db_path), patch('superlocalmemory.server.routes.helpers.get_active_profile', return_value='default'):
    client = TestClient(_make_app())
    client.post('/api/v3/forgetting/run', json={})
conn = sqlite3.connect(str(db_path))
post_score = conn.execute("SELECT retention_score FROM fact_retention WHERE lifecycle_zone = 'archive' AND profile_id = 'default'").fetchone()[0]
conn.close()
assert post_score == pre_score
```

## Next Steps


---

*Source: test_api_v33.py:358 | Complexity: Advanced | Last updated: 2026-05-05*