# How To: Binary Entry Fail Open On Miss

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Cache miss -> '{}', exit 0.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `ast`
- `hashlib`
- `json`
- `os`
- `random`
- `sqlite3`
- `string`
- `subprocess`
- `sys`
- `textwrap`
- `pathlib`
- `pytest`
- `build_entry`
- `superlocalmemory.core.topic_signature`
- `hmac`
- `time`
- `superlocalmemory.core.topic_signature`
- `re`
- `re`
- `re`
- `re`
- `emitted_entry`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: "Cache miss -> '{}', exit 0."

```python
"Cache miss -> '{}', exit 0."
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Assign home = value

```python
home = tmp_path / '.slm'
```

**Verification:**
```python
assert stdout == '{}'
```

### Step 3: Call home.mkdir()

```python
home.mkdir()
```

### Step 4: Assign dest = value

```python
dest = tmp_path / 'emitted_entry.py'
```

### Step 5: Call build_entry.emit_entry()

```python
build_entry.emit_entry(TOPIC_SRC, CACHE_SRC, dest)
```

### Step 6: Assign db = _seed_cache(...)

```python
db = _seed_cache(home, 'sess-x', 'deadbeefdeadbeef', 'other')
```

### Step 7: Assign unknown = _run_emitted(...)

```python
stdout, rc = _run_emitted(tmp_path, stdin_bytes=json.dumps({'session_id': 'sess-x', 'prompt': 'unrelated prompt'}).encode('utf-8'), env_overrides={'SLM_CACHE_DB': str(db)})
```

**Verification:**
```python
assert rc == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
"Cache miss -> '{}', exit 0."
home = tmp_path / '.slm'
home.mkdir()
dest = tmp_path / 'emitted_entry.py'
build_entry.emit_entry(TOPIC_SRC, CACHE_SRC, dest)
db = _seed_cache(home, 'sess-x', 'deadbeefdeadbeef', 'other')
stdout, rc = _run_emitted(tmp_path, stdin_bytes=json.dumps({'session_id': 'sess-x', 'prompt': 'unrelated prompt'}).encode('utf-8'), env_overrides={'SLM_CACHE_DB': str(db)})
assert rc == 0
assert stdout == '{}'
```

## Next Steps


---

*Source: test_entry_generator.py:414 | Complexity: Advanced | Last updated: 2026-05-05*