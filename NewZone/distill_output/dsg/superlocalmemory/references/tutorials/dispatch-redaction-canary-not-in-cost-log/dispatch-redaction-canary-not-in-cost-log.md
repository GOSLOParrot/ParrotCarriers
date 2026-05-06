# How To: Dispatch Redaction Canary Not In Cost Log

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: A synthetic GitHub PAT in the prompt must NOT appear in the cost log.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.evolution`
- `superlocalmemory.evolution.llm_dispatch`
- `superlocalmemory.core`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: learning_db, record_backend
```

## Step-by-Step Guide

### Step 1: 'A synthetic GitHub PAT in the prompt must NOT appear in the cost log.'

```python
'A synthetic GitHub PAT in the prompt must NOT appear in the cost log.'
```

**Verification:**
```python
assert record_backend, 'backend was not called'
```

### Step 2: Assign canary = value

```python
canary = 'ghp_' + 'A' * 36
```

**Verification:**
```python
assert canary not in dispatched
```

### Step 3: Assign prompt = value

```python
prompt = f'please help with this: {canary} and thanks'
```

**Verification:**
```python
assert rows, 'cost log row was not written'
```

### Step 4: Call _dispatch_llm()

```python
_dispatch_llm(prompt, model='claude-haiku-4-5', learning_db=learning_db, profile_id='default')
```

**Verification:**
```python
assert canary not in (profile_id or '')
```

### Step 5: Assign dispatched = value

```python
dispatched = record_backend[0]['prompt']
```

**Verification:**
```python
assert canary not in (model or '')
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(learning_db)
```

**Verification:**
```python
assert rows, 'cost log row was not written'
```

### Step 7: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT profile_id, model FROM evolution_llm_cost_log').fetchall()
```

### Step 8: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert canary not in (profile_id or '')
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, record_backend

# Workflow
'A synthetic GitHub PAT in the prompt must NOT appear in the cost log.'
canary = 'ghp_' + 'A' * 36
prompt = f'please help with this: {canary} and thanks'
_dispatch_llm(prompt, model='claude-haiku-4-5', learning_db=learning_db, profile_id='default')
assert record_backend, 'backend was not called'
dispatched = record_backend[0]['prompt']
assert canary not in dispatched
conn = sqlite3.connect(learning_db)
try:
    rows = conn.execute('SELECT profile_id, model FROM evolution_llm_cost_log').fetchall()
finally:
    conn.close()
assert rows, 'cost log row was not written'
for profile_id, model in rows:
    assert canary not in (profile_id or '')
    assert canary not in (model or '')
```

## Next Steps


---

*Source: test_llm_dispatch.py:235 | Complexity: Advanced | Last updated: 2026-05-05*