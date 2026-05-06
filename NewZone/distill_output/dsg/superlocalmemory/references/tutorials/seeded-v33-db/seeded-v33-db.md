# How To: Seeded V33 Db

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: DB with all V3.3 tables and seed data across all features.

Returns (db_path, fact_ids, block_ids, prompt_ids).

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'DB with all V3.3 tables and seed data across all features.\n\n    Returns (db_path, fact_ids, block_ids, prompt_ids).\n    '

```python
'DB with all V3.3 tables and seed data across all features.\n\n    Returns (db_path, fact_ids, block_ids, prompt_ids).\n    '
```

### Step 2: Assign db_path = _create_db(...)

```python
db_path = _create_db(tmp_path)
```

### Step 3: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 4: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 5: Assign fact_ids = _seed_retention(...)

```python
fact_ids = _seed_retention(conn)
```

### Step 6: Call _seed_quantization()

```python
_seed_quantization(conn)
```

### Step 7: Assign block_ids = _seed_ccq_blocks(...)

```python
block_ids = _seed_ccq_blocks(conn)
```

### Step 8: Assign prompt_ids = _seed_soft_prompts(...)

```python
prompt_ids = _seed_soft_prompts(conn)
```

### Step 9: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'DB with all V3.3 tables and seed data across all features.\n\n    Returns (db_path, fact_ids, block_ids, prompt_ids).\n    '
db_path = _create_db(tmp_path)
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
fact_ids = _seed_retention(conn)
_seed_quantization(conn)
block_ids = _seed_ccq_blocks(conn)
prompt_ids = _seed_soft_prompts(conn)
conn.close()
return (db_path, fact_ids, block_ids, prompt_ids)
```

## Next Steps


---

*Source: test_api_v33.py:199 | Complexity: Advanced | Last updated: 2026-05-05*