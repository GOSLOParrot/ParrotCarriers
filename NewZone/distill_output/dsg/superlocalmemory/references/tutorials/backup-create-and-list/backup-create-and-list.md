# How To: Backup Create And List

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test backup create and list

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.rate_limiter`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.cache_manager`
- `superlocalmemory.infra.auth_middleware`
- `superlocalmemory.infra.auth_middleware`
- `superlocalmemory.infra.auth_middleware`
- `superlocalmemory.infra.webhook_dispatcher`
- `superlocalmemory.infra.webhook_dispatcher`
- `superlocalmemory.infra.webhook_dispatcher`
- `superlocalmemory.infra.webhook_dispatcher`
- `superlocalmemory.infra.backup`
- `superlocalmemory.infra.backup`
- `superlocalmemory.infra.backup`
- `superlocalmemory.infra.backup`
- `superlocalmemory.infra.backup`
- `sqlite3`
- `superlocalmemory.infra.backup`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db_path = value

```python
db_path = tmp_path / 'memory.db'
```

**Verification:**
```python
assert name != ''
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

**Verification:**
```python
assert 'test' in name
```

### Step 3: Call conn.execute()

```python
conn.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
```

**Verification:**
```python
assert len(backups) >= 1
```

### Step 4: Call conn.commit()

```python
conn.commit()
```

**Verification:**
```python
assert backups[0]['type'] == 'memory'
```

### Step 5: Call conn.close()

```python
conn.close()
```

### Step 6: Assign backup = BackupManager(...)

```python
backup = BackupManager(base_dir=tmp_path)
```

### Step 7: Assign name = backup.create_backup(...)

```python
name = backup.create_backup(label='test')
```

**Verification:**
```python
assert name != ''
```

### Step 8: Assign backups = backup.list_backups(...)

```python
backups = backup.list_backups()
```

**Verification:**
```python
assert len(backups) >= 1
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
from superlocalmemory.infra.backup import BackupManager
import sqlite3
db_path = tmp_path / 'memory.db'
conn = sqlite3.connect(str(db_path))
conn.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
conn.commit()
conn.close()
backup = BackupManager(base_dir=tmp_path)
name = backup.create_backup(label='test')
assert name != ''
assert 'test' in name
backups = backup.list_backups()
assert len(backups) >= 1
assert backups[0]['type'] == 'memory'
```

## Next Steps


---

*Source: test_infra.py:243 | Complexity: Advanced | Last updated: 2026-05-05*