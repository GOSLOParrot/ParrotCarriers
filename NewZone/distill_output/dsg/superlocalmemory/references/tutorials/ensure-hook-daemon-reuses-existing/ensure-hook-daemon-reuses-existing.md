# How To: Ensure Hook Daemon Reuses Existing

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: ensure_hook_daemon() reuses existing running daemon.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `socket`
- `tempfile`
- `time`
- `pathlib`
- `unittest.mock`
- `pytest`
- `shutil`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `importlib`
- `sys`

**Setup Required:**
```python
# Fixtures: short_tmp
```

## Step-by-Step Guide

### Step 1: 'ensure_hook_daemon() reuses existing running daemon.'

```python
'ensure_hook_daemon() reuses existing running daemon.'
```

**Verification:**
```python
assert d2 is None
```

### Step 2: Assign sock_path = value

```python
sock_path = short_tmp / 'hook.sock'
```

### Step 3: Assign queue_db = value

```python
queue_db = short_tmp / 'q.db'
```

### Step 4: Assign d1 = HookDaemon(...)

```python
d1 = HookDaemon(sock_path=sock_path, queue_db_path=queue_db)
```

### Step 5: Call d1.start()

```python
d1.start()
```

### Step 6: Call time.sleep()

```python
time.sleep(0.1)
```

### Step 7: Assign d2 = ensure_hook_daemon(...)

```python
d2 = ensure_hook_daemon(sock_path=sock_path, queue_db_path=queue_db)
```

**Verification:**
```python
assert d2 is None
```

### Step 8: Call d1.stop()

```python
d1.stop()
```


## Complete Example

```python
# Setup
# Fixtures: short_tmp

# Workflow
'ensure_hook_daemon() reuses existing running daemon.'
from superlocalmemory.hooks.hook_daemon import HookDaemon, ensure_hook_daemon
sock_path = short_tmp / 'hook.sock'
queue_db = short_tmp / 'q.db'
d1 = HookDaemon(sock_path=sock_path, queue_db_path=queue_db)
d1.start()
time.sleep(0.1)
d2 = ensure_hook_daemon(sock_path=sock_path, queue_db_path=queue_db)
assert d2 is None
d1.stop()
```

## Next Steps


---

*Source: test_hook_daemon.py:165 | Complexity: Advanced | Last updated: 2026-05-05*