# How To: Cost Conn Cache Clears On Pid Drift

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: If the cache's owner pid no longer matches os.getpid(), the next
get_cost_conn must re-open — simulating a fork that missed the
register_at_fork handler.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `stat`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.hooks`
- `superlocalmemory.evolution`
- `superlocalmemory.evolution`
- `sqlite3`
- `superlocalmemory.hooks`
- `re`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: "If the cache's owner pid no longer matches os.getpid(), the next\n    get_cost_conn must re-open — simulating a fork that missed the\n    register_at_fork handler."

```python
"If the cache's owner pid no longer matches os.getpid(), the next\n    get_cost_conn must re-open — simulating a fork that missed the\n    register_at_fork handler."
```

**Verification:**
```python
assert db.resolve().samefile(list(ld._COST_CONN_CACHE.keys())[0]) or os.path.realpath(str(db)) in ld._COST_CONN_CACHE
```

### Step 2: Assign db = value

```python
db = tmp_path / 'learning.db'
```

**Verification:**
```python
assert conn1 is not conn2, 'cache failed to refresh on pid drift'
```

### Step 3: Assign conn1 = ld._get_cost_conn(...)

```python
conn1 = ld._get_cost_conn(db)
```

**Verification:**
```python
assert db.resolve().samefile(list(ld._COST_CONN_CACHE.keys())[0]) or os.path.realpath(str(db)) in ld._COST_CONN_CACHE
```

### Step 4: Assign ld._COST_CONN_OWNER_PID = value

```python
ld._COST_CONN_OWNER_PID = -1
```

### Step 5: Assign conn2 = ld._get_cost_conn(...)

```python
conn2 = ld._get_cost_conn(db)
```

**Verification:**
```python
assert conn1 is not conn2, 'cache failed to refresh on pid drift'
```

### Step 6: Call ld._close_cost_conns()

```python
ld._close_cost_conns()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
"If the cache's owner pid no longer matches os.getpid(), the next\n    get_cost_conn must re-open — simulating a fork that missed the\n    register_at_fork handler."
from superlocalmemory.evolution import llm_dispatch as ld
db = tmp_path / 'learning.db'
conn1 = ld._get_cost_conn(db)
assert db.resolve().samefile(list(ld._COST_CONN_CACHE.keys())[0]) or os.path.realpath(str(db)) in ld._COST_CONN_CACHE
ld._COST_CONN_OWNER_PID = -1
conn2 = ld._get_cost_conn(db)
assert conn1 is not conn2, 'cache failed to refresh on pid drift'
ld._close_cost_conns()
```

## Next Steps


---

*Source: test_s9_w2_security.py:163 | Complexity: Intermediate | Last updated: 2026-05-05*