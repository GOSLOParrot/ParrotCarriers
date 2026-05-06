# How To: Choose Never Raises On Missing Table

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: If bandit_arms is missing, choose() returns a valid BanditChoice.

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'If bandit_arms is missing, choose() returns a valid BanditChoice.'

```python
'If bandit_arms is missing, choose() returns a valid BanditChoice.'
```

**Verification:**
```python
assert choice.arm_id in ARM_CATALOG
```

### Step 2: Assign db = value

```python
db = tmp_path / 'empty.db'
```

### Step 3: Assign cache = _BanditCache(...)

```python
cache = _BanditCache(max_entries=4)
```

### Step 4: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(db, profile_id='p', cache=cache)
```

### Step 5: Assign choice = b.choose(...)

```python
choice = b.choose(_ctx(), query_id='noop')
```

**Verification:**
```python
assert choice.arm_id in ARM_CATALOG
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'If bandit_arms is missing, choose() returns a valid BanditChoice.'
db = tmp_path / 'empty.db'
cache = _BanditCache(max_entries=4)
b = ContextualBandit(db, profile_id='p', cache=cache)
choice = b.choose(_ctx(), query_id='noop')
assert choice.arm_id in ARM_CATALOG
```

## Next Steps


---

*Source: test_bandit_core.py:424 | Complexity: Intermediate | Last updated: 2026-05-05*