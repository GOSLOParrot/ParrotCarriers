# How To: Atomic Write No Partial

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test atomic write no partial

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `sqlite3`
- `sys`
- `pathlib`
- `pytest`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.hooks.adapter_base`
- `superlocalmemory.hooks.cursor_adapter`
- `superlocalmemory.hooks.context_payload`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `tests.test_adapters.conftest`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch, fake_recall
```

## Step-by-Step Guide

### Step 1: Assign adapter = _make_adapter(...)

```python
adapter = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
```

**Verification:**
```python
assert not target.exists()
```

### Step 2: Assign target = value

```python
target = adapter.target_path
```

### Step 3: Assign real_write = value

```python
real_write = os.write
```

### Step 4: Assign state = value

```python
state = {'calls': 0}
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.write', boom)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.write', real_write)
```

**Verification:**
```python
assert not target.exists()
```

### Step 7: Call adapter.sync()

```python
adapter.sync()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch, fake_recall

# Workflow
adapter = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
target = adapter.target_path
real_write = os.write
state = {'calls': 0}

def boom(fd, data):
    state['calls'] += 1
    raise OSError('simulated mid-write failure')
monkeypatch.setattr('os.write', boom)
with pytest.raises(OSError):
    adapter.sync()
monkeypatch.setattr('os.write', real_write)
assert not target.exists()
```

## Next Steps


---

*Source: test_cursor_adapter.py:132 | Complexity: Intermediate | Last updated: 2026-05-05*