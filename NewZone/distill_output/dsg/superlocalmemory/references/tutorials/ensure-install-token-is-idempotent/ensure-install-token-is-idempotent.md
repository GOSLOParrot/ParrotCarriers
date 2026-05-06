# How To: Ensure Install Token Is Idempotent

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Calling ensure_install_token twice must return the same token —
the O_EXCL path means the second call sees EEXIST and re-reads.

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
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Calling ensure_install_token twice must return the same token —\n    the O_EXCL path means the second call sees EEXIST and re-reads.'

```python
'Calling ensure_install_token twice must return the same token —\n    the O_EXCL path means the second call sees EEXIST and re-reads.'
```

**Verification:**
```python
assert first == second
```

### Step 2: Assign token_path = value

```python
token_path = tmp_path / '.install_token'
```

**Verification:**
```python
assert token_path.read_text(encoding='utf-8').strip() == first
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(sp, '_install_token_path', lambda: token_path)
```

**Verification:**
```python
assert mode == 384
```

### Step 4: Assign first = sp.ensure_install_token(...)

```python
first = sp.ensure_install_token()
```

### Step 5: Assign second = sp.ensure_install_token(...)

```python
second = sp.ensure_install_token()
```

**Verification:**
```python
assert first == second
```

### Step 6: Assign mode = stat.S_IMODE(...)

```python
mode = stat.S_IMODE(token_path.stat().st_mode)
```

**Verification:**
```python
assert mode == 384
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Calling ensure_install_token twice must return the same token —\n    the O_EXCL path means the second call sees EEXIST and re-reads.'
token_path = tmp_path / '.install_token'
monkeypatch.setattr(sp, '_install_token_path', lambda: token_path)
first = sp.ensure_install_token()
second = sp.ensure_install_token()
assert first == second
assert token_path.read_text(encoding='utf-8').strip() == first
if os.name == 'posix':
    mode = stat.S_IMODE(token_path.stat().st_mode)
    assert mode == 384
```

## Next Steps


---

*Source: test_s9_w2_security.py:120 | Complexity: Intermediate | Last updated: 2026-05-05*