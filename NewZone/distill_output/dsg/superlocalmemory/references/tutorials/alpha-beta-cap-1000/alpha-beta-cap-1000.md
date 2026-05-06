# How To: Alpha Beta Cap 1000

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: B2: alpha and beta clamp at 1000 regardless of update count.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `itertools`
- `secrets`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.storage.migration_runner`
- `datetime`
- `datetime`
- `time`

**Setup Required:**
```python
# Fixtures: bandit_db
```

## Step-by-Step Guide

### Step 1: 'B2: alpha and beta clamp at 1000 regardless of update count.'

```python
'B2: alpha and beta clamp at 1000 regardless of update count.'
```

**Verification:**
```python
assert alpha <= 1000.0
```

### Step 2: Assign cache = _BanditCache(...)

```python
cache = _BanditCache(max_entries=16)
```

**Verification:**
```python
assert beta <= 1000.0
```

### Step 3: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(bandit_db, profile_id='cap', cache=cache, alpha_cap=1000.0)
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(bandit_db))
```

### Step 5: Assign ch = b.choose(...)

```python
ch = b.choose(_ctx(), query_id=f'q-{i}')
```

### Step 6: Call b.update()

```python
b.update(ch.play_id, reward=1.0)
```

### Step 7: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT alpha, beta FROM bandit_arms WHERE profile_id = ?', ('cap',)).fetchall()
```

### Step 8: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert alpha <= 1000.0
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db

# Workflow
'B2: alpha and beta clamp at 1000 regardless of update count.'
cache = _BanditCache(max_entries=16)
b = ContextualBandit(bandit_db, profile_id='cap', cache=cache, alpha_cap=1000.0)
for i in range(1500):
    ch = b.choose(_ctx(), query_id=f'q-{i}')
    b.update(ch.play_id, reward=1.0)
conn = sqlite3.connect(str(bandit_db))
try:
    rows = conn.execute('SELECT alpha, beta FROM bandit_arms WHERE profile_id = ?', ('cap',)).fetchall()
finally:
    conn.close()
for alpha, beta in rows:
    assert alpha <= 1000.0
    assert beta <= 1000.0
```

## Next Steps


---

*Source: test_bandit_core.py:277 | Complexity: Advanced | Last updated: 2026-05-05*