# How To: Content Hash Skip Survives Restart

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: A3: durable skip driven by cross_platform_sync_log.content_sha256.

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

### Step 1: 'A3: durable skip driven by cross_platform_sync_log.content_sha256.'

```python
'A3: durable skip driven by cross_platform_sync_log.content_sha256.'
```

**Verification:**
```python
assert adapter1.sync() is True
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cp, '_now_iso', lambda: '2026-04-18T00:00:00+00:00')
```

**Verification:**
```python
assert adapter2.sync() is False
```

### Step 3: Assign adapter1 = _make_adapter(...)

```python
adapter1 = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
```

**Verification:**
```python
assert mtime_before == mtime_after
```

### Step 4: Assign adapter2 = CursorAdapter(...)

```python
adapter2 = CursorAdapter(scope='project', base_dir=tmp_path, sync_log_db=tmp_path / 'memory.db', recall_fn=fake_recall)
```

### Step 5: Call monkeypatch.setenv()

```python
monkeypatch.setenv('SLM_CURSOR_FORCE', '1')
```

### Step 6: Assign mtime_before = value

```python
mtime_before = adapter2.target_path.stat().st_mtime
```

**Verification:**
```python
assert adapter2.sync() is False
```

### Step 7: Assign mtime_after = value

```python
mtime_after = adapter2.target_path.stat().st_mtime
```

**Verification:**
```python
assert mtime_before == mtime_after
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch, fake_recall

# Workflow
'A3: durable skip driven by cross_platform_sync_log.content_sha256.'
from superlocalmemory.hooks import context_payload as cp
monkeypatch.setattr(cp, '_now_iso', lambda: '2026-04-18T00:00:00+00:00')
adapter1 = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
assert adapter1.sync() is True
adapter2 = CursorAdapter(scope='project', base_dir=tmp_path, sync_log_db=tmp_path / 'memory.db', recall_fn=fake_recall)
monkeypatch.setenv('SLM_CURSOR_FORCE', '1')
mtime_before = adapter2.target_path.stat().st_mtime
assert adapter2.sync() is False
mtime_after = adapter2.target_path.stat().st_mtime
assert mtime_before == mtime_after
```

## Next Steps


---

*Source: test_cursor_adapter.py:194 | Complexity: Intermediate | Last updated: 2026-05-05*