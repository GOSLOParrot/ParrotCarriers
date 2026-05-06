# How To: Bandit Choose Db Error Falls Back

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: If the posterior load raises, choose returns a valid BanditChoice.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `time`
- `dataclasses`
- `datetime`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.learning.ensemble`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.storage.migration_runner`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'If the posterior load raises, choose returns a valid BanditChoice.'

```python
'If the posterior load raises, choose returns a valid BanditChoice.'
```

**Verification:**
```python
assert ch.arm_id in ARM_CATALOG
```

### Step 2: Assign learning = value

```python
learning = tmp_path / 'learning.db'
```

### Step 3: Assign memory = value

```python
memory = tmp_path / 'memory.db'
```

### Step 4: Call apply_all()

```python
apply_all(learning, memory)
```

### Step 5: Assign cache = _BanditCache(...)

```python
cache = _BanditCache(max_entries=4)
```

### Step 6: Assign cache.get = _boom

```python
cache.get = _boom
```

### Step 7: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(learning, profile_id='p', cache=cache)
```

### Step 8: Assign ch = b.choose(...)

```python
ch = b.choose({'query_type': 'single_hop', 'entity_count': 0, 'time_bucket': 'morning'}, query_id='q')
```

**Verification:**
```python
assert ch.arm_id in ARM_CATALOG
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'If the posterior load raises, choose returns a valid BanditChoice.'
learning = tmp_path / 'learning.db'
memory = tmp_path / 'memory.db'
apply_all(learning, memory)
cache = _BanditCache(max_entries=4)

def _boom(profile, stratum, loader):
    raise sqlite3.OperationalError('mocked')
cache.get = _boom
b = ContextualBandit(learning, profile_id='p', cache=cache)
ch = b.choose({'query_type': 'single_hop', 'entity_count': 0, 'time_bucket': 'morning'}, query_id='q')
assert ch.arm_id in ARM_CATALOG
```

## Next Steps


---

*Source: test_bandit_supplementary.py:414 | Complexity: Advanced | Last updated: 2026-05-05*