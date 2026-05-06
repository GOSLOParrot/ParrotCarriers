# How To: Binary Entry Envelope On Hit

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: H14: on a cache hit, main() outputs the LLD-01 §4.3 envelope.

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

### Step 1: 'H14: on a cache hit, main() outputs the LLD-01 §4.3 envelope.'

```python
'H14: on a cache hit, main() outputs the LLD-01 §4.3 envelope.'
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
assert 'hookSpecificOutput' in doc
```

### Step 3: Call home.mkdir()

```python
home.mkdir()
```

**Verification:**
```python
assert doc['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
```

### Step 4: Assign dest = value

```python
dest = tmp_path / 'emitted_entry.py'
```

**Verification:**
```python
assert doc['hookSpecificOutput']['additionalContext'] == 'cached context for tests'
```

### Step 5: Call build_entry.emit_entry()

```python
build_entry.emit_entry(TOPIC_SRC, CACHE_SRC, dest)
```

### Step 6: Assign prompt = 'build the login button in React'

```python
prompt = 'build the login button in React'
```

### Step 7: Assign sig = compute_topic_signature(...)

```python
sig = compute_topic_signature(prompt)
```

### Step 8: Assign db = _seed_cache(...)

```python
db = _seed_cache(home, 'sess-123', sig, 'cached context for tests')
```

### Step 9: Assign unknown = _run_emitted(...)

```python
stdout, rc = _run_emitted(tmp_path, stdin_bytes=json.dumps({'session_id': 'sess-123', 'prompt': prompt}).encode('utf-8'), env_overrides={'SLM_CACHE_DB': str(db)})
```

**Verification:**
```python
assert rc == 0
```

### Step 10: Assign doc = json.loads(...)

```python
doc = json.loads(stdout)
```

**Verification:**
```python
assert 'hookSpecificOutput' in doc
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'H14: on a cache hit, main() outputs the LLD-01 §4.3 envelope.'
home = tmp_path / '.slm'
home.mkdir()
dest = tmp_path / 'emitted_entry.py'
build_entry.emit_entry(TOPIC_SRC, CACHE_SRC, dest)
from superlocalmemory.core.topic_signature import compute_topic_signature
prompt = 'build the login button in React'
sig = compute_topic_signature(prompt)
db = _seed_cache(home, 'sess-123', sig, 'cached context for tests')
stdout, rc = _run_emitted(tmp_path, stdin_bytes=json.dumps({'session_id': 'sess-123', 'prompt': prompt}).encode('utf-8'), env_overrides={'SLM_CACHE_DB': str(db)})
assert rc == 0
doc = json.loads(stdout)
assert 'hookSpecificOutput' in doc
assert doc['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
assert doc['hookSpecificOutput']['additionalContext'] == 'cached context for tests'
```

## Next Steps


---

*Source: test_entry_generator.py:339 | Complexity: Advanced | Last updated: 2026-05-05*