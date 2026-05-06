# How To: Dry Run Does Not Modify Db

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: With --dry-run, the runner MUST NOT create any rows.

Exit code reflects whatever apply_all reports. Contract under test
here is the 'no writes' guarantee, independent of exit code.

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

### Step 1: "With --dry-run, the runner MUST NOT create any rows.\n\n    Exit code reflects whatever apply_all reports. Contract under test\n    here is the 'no writes' guarantee, independent of exit code.\n    "

```python
"With --dry-run, the runner MUST NOT create any rows.\n\n    Exit code reflects whatever apply_all reports. Contract under test\n    here is the 'no writes' guarantee, independent of exit code.\n    "
```

**Verification:**
```python
assert count == 0
```

### Step 2: Assign unknown = dual_db

```python
learning, memory = dual_db
```

### Step 3: Call cmd_db_migrate()

```python
cmd_db_migrate(_make_args(learning, memory, dry_run=True))
```

### Step 4: Call capsys.readouterr()

```python
capsys.readouterr()
```

### Step 5: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(learning)
```

### Step 6: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migration_log'").fetchone()
```

### Step 7: Call conn.close()

```python
conn.close()
```

### Step 8: Assign count = value

```python
count = conn.execute('SELECT COUNT(*) FROM migration_log').fetchone()[0]
```

**Verification:**
```python
assert count == 0
```


## Complete Example

```python
# Setup
# Fixtures: dual_db, capsys

# Workflow
"With --dry-run, the runner MUST NOT create any rows.\n\n    Exit code reflects whatever apply_all reports. Contract under test\n    here is the 'no writes' guarantee, independent of exit code.\n    "
from superlocalmemory.cli.db_migrate import cmd_db_migrate
learning, memory = dual_db
cmd_db_migrate(_make_args(learning, memory, dry_run=True))
capsys.readouterr()
conn = sqlite3.connect(learning)
try:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migration_log'").fetchone()
    if row is not None:
        count = conn.execute('SELECT COUNT(*) FROM migration_log').fetchone()[0]
        assert count == 0
finally:
    conn.close()
```

## Next Steps


---

*Source: test_db_migrate.py:161 | Complexity: Advanced | Last updated: 2026-05-05*