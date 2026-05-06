# How To: Sec M6 Ram Lock Parent Dir Is 0700

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test sec m6 ram lock parent dir is 0700

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `stat`
- `sys`
- `pathlib`
- `pytest`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign parent = value

```python
parent = tmp_path / 'slm-home'
```

**Verification:**
```python
assert parent.is_dir()
```

### Step 2: Assign lock = value

```python
lock = parent / 'ram_lock.sem'
```

**Verification:**
```python
assert mode == 448, oct(mode)
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ram_lock, 'RAM_LOCK_PATH', lock)
```

**Verification:**
```python
assert mode == 448, oct(mode)
```

### Step 4: Assign mode = stat.S_IMODE(...)

```python
mode = stat.S_IMODE(parent.stat().st_mode)
```

**Verification:**
```python
assert mode == 448, oct(mode)
```

### Step 5: Assign mode = stat.S_IMODE(...)

```python
mode = stat.S_IMODE(parent.stat().st_mode)
```

**Verification:**
```python
assert mode == 448, oct(mode)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
from superlocalmemory.core import ram_lock
parent = tmp_path / 'slm-home'
lock = parent / 'ram_lock.sem'
monkeypatch.setattr(ram_lock, 'RAM_LOCK_PATH', lock)
with ram_lock.ram_reservation('stage8-m6', required_mb=1):
    assert parent.is_dir()
    mode = stat.S_IMODE(parent.stat().st_mode)
    assert mode == 448, oct(mode)
mode = stat.S_IMODE(parent.stat().st_mode)
assert mode == 448, oct(mode)
```

## Next Steps


---

*Source: test_stage8_ram_lock_parent_perms.py:26 | Complexity: Intermediate | Last updated: 2026-05-05*