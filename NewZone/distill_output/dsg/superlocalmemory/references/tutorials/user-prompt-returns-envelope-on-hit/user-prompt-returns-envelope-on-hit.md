# How To: User Prompt Returns Envelope On Hit

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test user prompt returns envelope on hit

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `sys`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.hooks`
- `superlocalmemory.core.topic_signature`
- `urllib.request`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.core.topic_signature`
- `urllib.request`
- `urllib.request`
- `urllib.request`

**Setup Required:**
```python
# Fixtures: home, seeded_cache, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign prompt = 'please refactor the context cache writer into smaller functions'

```python
prompt = 'please refactor the context cache writer into smaller functions'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Assign sig = compute_topic_signature(...)

```python
sig = compute_topic_signature(prompt)
```

**Verification:**
```python
assert 'hookSpecificOutput' in parsed
```

### Step 3: Assign cache = cc.ContextCache(...)

```python
cache = cc.ContextCache(db_path=home / 'active_brain_cache.db', home_dir=home)
```

**Verification:**
```python
assert inner['hookEventName'] == 'UserPromptSubmit'
```

### Step 4: Assign payload = json.dumps(...)

```python
payload = json.dumps({'session_id': 'sess-envelope', 'prompt': prompt})
```

**Verification:**
```python
assert 'prior work' in inner['additionalContext']
```

### Step 5: Assign unknown = _run_hook(...)

```python
rc, out = _run_hook(user_prompt_hook.main, payload, monkeypatch)
```

**Verification:**
```python
assert '[BEGIN UNTRUSTED SLM CONTEXT' in ac
```

### Step 6: Assign parsed = json.loads(...)

```python
parsed = json.loads(out)
```

**Verification:**
```python
assert '[END UNTRUSTED SLM CONTEXT]' in ac
```

### Step 7: Assign inner = value

```python
inner = parsed['hookSpecificOutput']
```

**Verification:**
```python
assert begin_idx < ac.index('prior work') < end_idx
```

### Step 8: Assign ac = value

```python
ac = inner['additionalContext']
```

**Verification:**
```python
assert '[BEGIN UNTRUSTED SLM CONTEXT' in ac
```

### Step 9: Assign begin_idx = ac.index(...)

```python
begin_idx = ac.index('[BEGIN UNTRUSTED SLM CONTEXT')
```

### Step 10: Assign end_idx = ac.index(...)

```python
end_idx = ac.index('[END UNTRUSTED SLM CONTEXT]')
```

**Verification:**
```python
assert begin_idx < ac.index('prior work') < end_idx
```

### Step 11: Call cache.upsert()

```python
cache.upsert(cc.CacheEntry(session_id='sess-envelope', topic_sig=sig, content='prior work: split ContextCache into writer/reader', fact_ids=['f42'], provenance='tool_observation', computed_at=int(time.time())))
```

### Step 12: Call cache.close()

```python
cache.close()
```


## Complete Example

```python
# Setup
# Fixtures: home, seeded_cache, monkeypatch

# Workflow
from superlocalmemory.core.topic_signature import compute_topic_signature
prompt = 'please refactor the context cache writer into smaller functions'
sig = compute_topic_signature(prompt)
cache = cc.ContextCache(db_path=home / 'active_brain_cache.db', home_dir=home)
try:
    cache.upsert(cc.CacheEntry(session_id='sess-envelope', topic_sig=sig, content='prior work: split ContextCache into writer/reader', fact_ids=['f42'], provenance='tool_observation', computed_at=int(time.time())))
finally:
    cache.close()
payload = json.dumps({'session_id': 'sess-envelope', 'prompt': prompt})
rc, out = _run_hook(user_prompt_hook.main, payload, monkeypatch)
assert rc == 0
parsed = json.loads(out)
assert 'hookSpecificOutput' in parsed
inner = parsed['hookSpecificOutput']
assert inner['hookEventName'] == 'UserPromptSubmit'
assert 'prior work' in inner['additionalContext']
ac = inner['additionalContext']
assert '[BEGIN UNTRUSTED SLM CONTEXT' in ac
assert '[END UNTRUSTED SLM CONTEXT]' in ac
begin_idx = ac.index('[BEGIN UNTRUSTED SLM CONTEXT')
end_idx = ac.index('[END UNTRUSTED SLM CONTEXT]')
assert begin_idx < ac.index('prior work') < end_idx
```

## Next Steps


---

*Source: test_hook_handlers.py:85 | Complexity: Advanced | Last updated: 2026-05-05*