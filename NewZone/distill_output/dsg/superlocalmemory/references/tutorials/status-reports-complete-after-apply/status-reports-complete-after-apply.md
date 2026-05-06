# How To: Status Reports Complete After Apply

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test status reports complete after apply

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
# Fixtures: dual_db, capsys
```

## Step-by-Step Guide

### Step 1: Assign unknown = dual_db

```python
learning, memory = dual_db
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Assign rc = cmd_db_migrate(...)

```python
rc = cmd_db_migrate(_make_args(learning, memory))
```

**Verification:**
```python
assert rc_status == 0
```

### Step 3: Call capsys.readouterr()

```python
capsys.readouterr()
```

**Verification:**
```python
assert 'complete' in report
```

### Step 4: Assign rc_status = cmd_db_migrate(...)

```python
rc_status = cmd_db_migrate(_make_args(learning, memory, status=True))
```

**Verification:**
```python
assert rc_status == 0
```

### Step 5: Assign report = value

```python
report = capsys.readouterr().out
```

**Verification:**
```python
assert 'complete' in report
```


## Complete Example

```python
# Setup
# Fixtures: dual_db, capsys

# Workflow
from superlocalmemory.cli.db_migrate import cmd_db_migrate
learning, memory = dual_db
rc = cmd_db_migrate(_make_args(learning, memory))
assert rc == 0
capsys.readouterr()
rc_status = cmd_db_migrate(_make_args(learning, memory, status=True))
assert rc_status == 0
report = capsys.readouterr().out
assert 'complete' in report
```

## Next Steps


---

*Source: test_db_migrate.py:102 | Complexity: Intermediate | Last updated: 2026-05-05*