# How To: V2 Upgrade Accepted

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Instantiate _make_fake_v2_migrator_module: test v2 upgrade accepted

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sys`
- `types`
- `unittest.mock`
- `pytest`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.cli.migrate_cmd`
- `superlocalmemory.cli`
- `inspect`
- `superlocalmemory.cli`
- `inspect`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.storage.v2_migrator`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.storage.v2_migrator`
- `superlocalmemory.cli.post_install`
- `superlocalmemory.storage.v2_migrator`
- `superlocalmemory.cli.migrate_cmd`
- `superlocalmemory.cli.migrate_cmd`
- `superlocalmemory.cli.migrate_cmd`
- `superlocalmemory.cli.migrate_cmd`
- `superlocalmemory.cli.migrate_cmd`
- `superlocalmemory.cli.migrate_cmd`

**Setup Required:**
```python
# Fixtures: capsys
```

## Step-by-Step Guide

### Step 1: Assign fake_mod = _make_fake_v2_migrator_module(...)

```python
fake_mod = _make_fake_v2_migrator_module(detect_v2=True, is_already_migrated=False, v2_stats={'db_path': '/home/.claude-memory/memory.db', 'memory_count': 42, 'profile_count': 2}, migrate_result={'success': True, 'steps': ['backup', 'schema', 'reindex'], 'v3_db': '/v3.db', 'backup_db': '/bak.db'})
```


## Complete Example

```python
# Setup
# Fixtures: capsys

# Workflow
fake_mod = _make_fake_v2_migrator_module(detect_v2=True, is_already_migrated=False, v2_stats={'db_path': '/home/.claude-memory/memory.db', 'memory_count': 42, 'profile_count': 2}, migrate_result={'success': True, 'steps': ['backup', 'schema', 'reindex'], 'v3_db': '/v3.db', 'backup_db': '/bak.db'})
```

## Next Steps


---

*Source: test_post_install.py:115 | Complexity: Beginner | Last updated: 2026-05-05*