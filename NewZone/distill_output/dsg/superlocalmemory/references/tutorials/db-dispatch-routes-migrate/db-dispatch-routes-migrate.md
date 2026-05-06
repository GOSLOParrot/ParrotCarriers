# How To: Db Dispatch Routes Migrate

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: `_cmd_db_dispatch` with db_command='migrate' must invoke
cmd_db_migrate.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `argparse`
- `pathlib`
- `pytest`
- `superlocalmemory.cli.db_migrate`
- `superlocalmemory.cli.db_migrate`
- `superlocalmemory.cli`
- `superlocalmemory.cli.db_migrate`
- `superlocalmemory.cli.db_migrate`
- `superlocalmemory.cli.db_migrate`
- `superlocalmemory.cli.db_migrate`
- `superlocalmemory.cli`
- `superlocalmemory.cli`
- `superlocalmemory.cli`
- `superlocalmemory.cli`
- `superlocalmemory.cli`
- `superlocalmemory.cli`

**Setup Required:**
```python
# Fixtures: monkeypatch, dual_db, capsys
```

## Step-by-Step Guide

### Step 1: "`_cmd_db_dispatch` with db_command='migrate' must invoke\n    cmd_db_migrate."

```python
"`_cmd_db_dispatch` with db_command='migrate' must invoke\n    cmd_db_migrate."
```

**Verification:**
```python
assert called['args'] is args
```

### Step 2: Assign called = value

```python
called = {}
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.cli.db_migrate.cmd_db_migrate', fake_handler)
```

### Step 4: Assign unknown = dual_db

```python
learning, memory = dual_db
```

### Step 5: Assign args = _make_args(...)

```python
args = _make_args(learning, memory)
```

### Step 6: Call cmd_mod._cmd_db_dispatch()

```python
cmd_mod._cmd_db_dispatch(args)
```

**Verification:**
```python
assert called['args'] is args
```

### Step 7: Assign unknown = args

```python
called['args'] = args
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch, dual_db, capsys

# Workflow
"`_cmd_db_dispatch` with db_command='migrate' must invoke\n    cmd_db_migrate."
from superlocalmemory.cli import commands as cmd_mod
called = {}

def fake_handler(args):
    called['args'] = args
    return 0
monkeypatch.setattr('superlocalmemory.cli.db_migrate.cmd_db_migrate', fake_handler)
learning, memory = dual_db
args = _make_args(learning, memory)
cmd_mod._cmd_db_dispatch(args)
assert called['args'] is args
```

## Next Steps


---

*Source: test_db_migrate.py:252 | Complexity: Intermediate | Last updated: 2026-05-05*