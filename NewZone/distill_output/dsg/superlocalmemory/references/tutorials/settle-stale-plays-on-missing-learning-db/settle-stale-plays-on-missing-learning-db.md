# How To: Settle Stale Plays On Missing Learning Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Bad learning path → returns 0 without raising.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `unicodedata`
- `datetime`
- `pathlib`
- `pytest`
- `superlocalmemory.core.topic_signature`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.storage.migration_runner`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Bad learning path → returns 0 without raising.'

```python
'Bad learning path → returns 0 without raising.'
```

**Verification:**
```python
assert n == 0
```

### Step 2: Assign ghost = value

```python
ghost = tmp_path / 'nope.db'
```

### Step 3: Assign memory = _bootstrap_memory_db(...)

```python
memory = _bootstrap_memory_db(tmp_path)
```

### Step 4: Assign bad = tmp_path

```python
bad = tmp_path
```

### Step 5: Assign n = settle_stale_plays(...)

```python
n = settle_stale_plays(PROFILE, bad, memory, now=datetime.now(timezone.utc))
```

**Verification:**
```python
assert n == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Bad learning path → returns 0 without raising.'
ghost = tmp_path / 'nope.db'
memory = _bootstrap_memory_db(tmp_path)
bad = tmp_path
n = settle_stale_plays(PROFILE, bad, memory, now=datetime.now(timezone.utc))
assert n == 0
```

## Next Steps


---

*Source: test_reward_proxy.py:305 | Complexity: Intermediate | Last updated: 2026-05-05*