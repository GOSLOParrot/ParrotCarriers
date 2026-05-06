# How To: Sync Log Target Path Sha256 Full Length Not Raw

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: A7: sync log stores SHA-256 (full 64-hex), never the raw absolute path.

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

### Step 1: 'A7: sync log stores SHA-256 (full 64-hex), never the raw absolute path.'

```python
'A7: sync log stores SHA-256 (full 64-hex), never the raw absolute path.'
```

**Verification:**
```python
assert rows, 'expected at least one sync log row'
```

### Step 2: Assign adapter = _make_adapter(...)

```python
adapter = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
```

**Verification:**
```python
assert len(sha) == 64, f'target_path_sha256 must be 64 hex, got {len(sha)}'
```

### Step 3: Call adapter.sync()

```python
adapter.sync()
```

**Verification:**
```python
assert all((c in '0123456789abcdef' for c in sha))
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(tmp_path / 'memory.db'))
```

**Verification:**
```python
assert sha != raw_path
```

### Step 5: Assign raw_path = str(...)

```python
raw_path = str(adapter.target_path)
```

**Verification:**
```python
assert os.sep not in sha and '/' not in sha
```

### Step 6: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT target_path_sha256, target_basename FROM cross_platform_sync_log').fetchall()
```

**Verification:**
```python
assert basename == adapter.target_path.name
```

### Step 7: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert len(sha) == 64, f'target_path_sha256 must be 64 hex, got {len(sha)}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch, fake_recall

# Workflow
'A7: sync log stores SHA-256 (full 64-hex), never the raw absolute path.'
adapter = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
adapter.sync()
conn = sqlite3.connect(str(tmp_path / 'memory.db'))
try:
    rows = conn.execute('SELECT target_path_sha256, target_basename FROM cross_platform_sync_log').fetchall()
finally:
    conn.close()
assert rows, 'expected at least one sync log row'
raw_path = str(adapter.target_path)
for sha, basename in rows:
    assert len(sha) == 64, f'target_path_sha256 must be 64 hex, got {len(sha)}'
    assert all((c in '0123456789abcdef' for c in sha))
    assert sha != raw_path
    assert os.sep not in sha and '/' not in sha
    assert basename == adapter.target_path.name
```

## Next Steps


---

*Source: test_cursor_adapter.py:216 | Complexity: Advanced | Last updated: 2026-05-05*