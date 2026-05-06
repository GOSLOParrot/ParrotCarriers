# How To: Secret Canary In Prompt Never Appears In Cost Log Row

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Raw GitHub PAT must be redacted before reaching backend AND not
persisted anywhere in the cost log row.

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

### Step 1: 'Raw GitHub PAT must be redacted before reaching backend AND not\n    persisted anywhere in the cost log row.'

```python
'Raw GitHub PAT must be redacted before reaching backend AND not\n    persisted anywhere in the cost log row.'
```

**Verification:**
```python
assert record_backend
```

### Step 2: Assign canary = value

```python
canary = 'ghp_' + 'B' * 36
```

**Verification:**
```python
assert canary not in record_backend[0]['prompt']
```

### Step 3: Call _dispatch_llm()

```python
_dispatch_llm(f'token: {canary}', model='claude-haiku-4-5', learning_db=learning_db, profile_id='default', cycle_id='cyc-sec-1')
```

**Verification:**
```python
assert canary not in joined
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(learning_db)
```

### Step 5: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT profile_id, model, cycle_id, tokens_in, tokens_out FROM evolution_llm_cost_log').fetchall()
```

### Step 6: Call conn.close()

```python
conn.close()
```

### Step 7: Assign joined = unknown.join(...)

```python
joined = ' '.join((str(c) for c in row))
```

**Verification:**
```python
assert canary not in joined
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, record_backend

# Workflow
'Raw GitHub PAT must be redacted before reaching backend AND not\n    persisted anywhere in the cost log row.'
canary = 'ghp_' + 'B' * 36
_dispatch_llm(f'token: {canary}', model='claude-haiku-4-5', learning_db=learning_db, profile_id='default', cycle_id='cyc-sec-1')
assert record_backend
assert canary not in record_backend[0]['prompt']
conn = sqlite3.connect(learning_db)
try:
    rows = conn.execute('SELECT profile_id, model, cycle_id, tokens_in, tokens_out FROM evolution_llm_cost_log').fetchall()
finally:
    conn.close()
for row in rows:
    joined = ' '.join((str(c) for c in row))
    assert canary not in joined
```

## Next Steps


---

*Source: test_llm_dispatch.py:400 | Complexity: Advanced | Last updated: 2026-05-05*