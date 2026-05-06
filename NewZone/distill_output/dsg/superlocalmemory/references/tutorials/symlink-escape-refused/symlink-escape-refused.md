# How To: Symlink Escape Refused

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test symlink escape refused

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

### Step 1: Assign outside = value

```python
outside = tmp_path / 'outside'
```

**Verification:**
```python
assert adapter.sync() is False
```

### Step 2: Call outside.mkdir()

```python
outside.mkdir()
```

### Step 3: Assign target_parent = value

```python
target_parent = tmp_path / 'base' / '.cursor' / 'rules'
```

### Step 4: Call target_parent.mkdir()

```python
target_parent.mkdir(parents=True)
```

### Step 5: Assign link = value

```python
link = target_parent / 'slm-active-brain.mdc'
```

### Step 6: Call link.symlink_to()

```python
link.symlink_to(outside / 'gotcha.mdc')
```

### Step 7: Call monkeypatch.setenv()

```python
monkeypatch.setenv('SLM_CURSOR_FORCE', '1')
```

### Step 8: Assign adapter = CursorAdapter(...)

```python
adapter = CursorAdapter(scope='project', base_dir=tmp_path / 'base', sync_log_db=tmp_path / 'memory.db', recall_fn=fake_recall)
```

**Verification:**
```python
assert adapter.sync() is False
```

### Step 9: Call pytest.skip()

```python
pytest.skip('symlink-escape semantics differ on Windows')
```

### Step 10: Assign _ = value

```python
_ = adapter.target_path
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch, fake_recall

# Workflow
outside = tmp_path / 'outside'
outside.mkdir()
target_parent = tmp_path / 'base' / '.cursor' / 'rules'
target_parent.mkdir(parents=True)
if sys.platform == 'win32':
    pytest.skip('symlink-escape semantics differ on Windows')
link = target_parent / 'slm-active-brain.mdc'
link.symlink_to(outside / 'gotcha.mdc')
monkeypatch.setenv('SLM_CURSOR_FORCE', '1')
adapter = CursorAdapter(scope='project', base_dir=tmp_path / 'base', sync_log_db=tmp_path / 'memory.db', recall_fn=fake_recall)
with pytest.raises(PathTraversalError):
    _ = adapter.target_path
assert adapter.sync() is False
```

## Next Steps


---

*Source: test_cursor_adapter.py:85 | Complexity: Advanced | Last updated: 2026-05-05*