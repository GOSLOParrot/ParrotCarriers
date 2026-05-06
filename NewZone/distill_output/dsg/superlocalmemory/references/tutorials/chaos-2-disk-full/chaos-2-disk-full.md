# How To: Chaos 2 Disk Full

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Graceful QueueFullError / OperationalError; no corruption;
resumes when space freed. Requires a writable tmpfs-like mount to
fill safely; skip if the host filesystem is too large.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `sys`
- `tempfile`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core.recall_queue`
- `resource`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Graceful QueueFullError / OperationalError; no corruption;\n    resumes when space freed. Requires a writable tmpfs-like mount to\n    fill safely; skip if the host filesystem is too large.'

```python
'Graceful QueueFullError / OperationalError; no corruption;\n    resumes when space freed. Requires a writable tmpfs-like mount to\n    fill safely; skip if the host filesystem is too large.'
```

**Verification:**
```python
assert 'No space' in str(exc) or '28' in str(exc), f'unexpected error: {exc}'
```

### Step 2: Assign filler = value

```python
filler = tmp_path / 'filler.bin'
```

### Step 3: Assign written = 0

```python
written = 0
```

### Step 4: Assign chunk = value

```python
chunk = b'\x00' * (1024 * 1024)
```

**Verification:**
```python
assert 'No space' in str(exc) or '28' in str(exc), f'unexpected error: {exc}'
```

### Step 5: Call filler.unlink()

```python
filler.unlink()
```

### Step 6: Call f.write()

```python
f.write(chunk)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Graceful QueueFullError / OperationalError; no corruption;\n    resumes when space freed. Requires a writable tmpfs-like mount to\n    fill safely; skip if the host filesystem is too large.'
filler = tmp_path / 'filler.bin'
try:
    with open(filler, 'wb') as f:
        written = 0
        chunk = b'\x00' * (1024 * 1024)
        while written < 512 * 1024 * 1024:
            f.write(chunk)
            written += len(chunk)
except OSError as exc:
    assert 'No space' in str(exc) or '28' in str(exc), f'unexpected error: {exc}'
finally:
    if filler.exists():
        filler.unlink()
```

## Next Steps


---

*Source: test_chaos_queue.py:131 | Complexity: Advanced | Last updated: 2026-05-05*