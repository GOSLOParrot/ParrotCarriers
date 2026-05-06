# How To: Engine Db

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, pytest, workflow, integration

## Overview

Workflow: Create a seeded DB and point SLMConfig at it.

Also monkeypatches DEFAULT_BASE_DIR so SLMConfig.load() reads from tmp_path.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `threading`
- `uuid`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.storage.schema_v32`
- `superlocalmemory.storage`
- `superlocalmemory.server.routes.helpers`
- `fastapi`
- `superlocalmemory.server.routes.entity`
- `fastapi.testclient`
- `fastapi.testclient`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes`
- `superlocalmemory.core.engine`
- `fastapi`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes.helpers`
- `superlocalmemory.server.routes`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Create a seeded DB and point SLMConfig at it.\n\n    Also monkeypatches DEFAULT_BASE_DIR so SLMConfig.load() reads from tmp_path.\n    '

```python
'Create a seeded DB and point SLMConfig at it.\n\n    Also monkeypatches DEFAULT_BASE_DIR so SLMConfig.load() reads from tmp_path.\n    '
```

### Step 2: Assign db_path = value

```python
db_path = tmp_path / 'memory.db'
```

### Step 3: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 4: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 5: Call schema.create_all_tables()

```python
schema.create_all_tables(conn)
```

### Step 6: Call _setup_v32_tables()

```python
_setup_v32_tables(conn)
```

### Step 7: Call conn.execute()

```python
conn.execute("INSERT OR IGNORE INTO profiles (profile_id, name, description) VALUES ('default', 'default', 'test')")
```

### Step 8: Call _seed_entity()

```python
_seed_entity(conn, 'Varun')
```

### Step 9: Call _seed_entity()

```python
_seed_entity(conn, 'Qualixar', 'organization')
```

### Step 10: Call conn.commit()

```python
conn.commit()
```

### Step 11: Call conn.close()

```python
conn.close()
```

### Step 12: Call monkeypatch.setenv()

```python
monkeypatch.setenv('SLM_BASE_DIR', str(tmp_path))
```

### Step 13: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.core.config.DEFAULT_BASE_DIR', tmp_path)
```

### Step 14: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.server.routes.helpers.MEMORY_DIR', tmp_path)
```

### Step 15: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.server.routes.helpers.DB_PATH', db_path)
```

### Step 16: Assign _helpers._last_engine_failure = 0.0

```python
_helpers._last_engine_failure = 0.0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Create a seeded DB and point SLMConfig at it.\n\n    Also monkeypatches DEFAULT_BASE_DIR so SLMConfig.load() reads from tmp_path.\n    '
from superlocalmemory.storage import schema
db_path = tmp_path / 'memory.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
schema.create_all_tables(conn)
_setup_v32_tables(conn)
conn.execute("INSERT OR IGNORE INTO profiles (profile_id, name, description) VALUES ('default', 'default', 'test')")
_seed_entity(conn, 'Varun')
_seed_entity(conn, 'Qualixar', 'organization')
conn.commit()
conn.close()
monkeypatch.setenv('SLM_BASE_DIR', str(tmp_path))
monkeypatch.setattr('superlocalmemory.core.config.DEFAULT_BASE_DIR', tmp_path)
monkeypatch.setattr('superlocalmemory.server.routes.helpers.MEMORY_DIR', tmp_path)
monkeypatch.setattr('superlocalmemory.server.routes.helpers.DB_PATH', db_path)
import superlocalmemory.server.routes.helpers as _helpers
if hasattr(_helpers, '_last_engine_failure'):
    _helpers._last_engine_failure = 0.0
return tmp_path
```

## Next Steps


---

*Source: test_engine_lifecycle.py:61 | Complexity: Advanced | Last updated: 2026-05-05*