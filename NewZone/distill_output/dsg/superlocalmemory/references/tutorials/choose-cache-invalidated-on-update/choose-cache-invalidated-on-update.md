# How To: Choose Cache Invalidated On Update

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: B5: next choose() after update re-reads posteriors from DB.

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

### Step 1: 'B5: next choose() after update re-reads posteriors from DB.'

```python
'B5: next choose() after update re-reads posteriors from DB.'
```

**Verification:**
```python
assert loader_calls['n'] == 1
```

### Step 2: Assign cache = _BanditCache(...)

```python
cache = _BanditCache(max_entries=16)
```

**Verification:**
```python
assert loader_calls['n'] == 1
```

### Step 3: Assign loader_calls = value

```python
loader_calls = {'n': 0}
```

**Verification:**
```python
assert b.update(ch1.play_id, reward=1.0) is True
```

### Step 4: Assign real = value

```python
real = cache.get
```

**Verification:**
```python
assert loader_calls['n'] == 2
```

### Step 5: Assign cache.get = _counting_get

```python
cache.get = _counting_get
```

### Step 6: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(bandit_db, profile_id='inv', cache=cache)
```

### Step 7: Assign ch1 = b.choose(...)

```python
ch1 = b.choose(_ctx(), query_id='q1')
```

**Verification:**
```python
assert loader_calls['n'] == 1
```

### Step 8: Call b.choose()

```python
b.choose(_ctx(), query_id='q2')
```

**Verification:**
```python
assert loader_calls['n'] == 1
```

### Step 9: Call b.choose()

```python
b.choose(_ctx(), query_id='q3')
```

**Verification:**
```python
assert loader_calls['n'] == 2
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db

# Workflow
'B5: next choose() after update re-reads posteriors from DB.'
cache = _BanditCache(max_entries=16)
loader_calls = {'n': 0}
real = cache.get

def _counting_get(profile, stratum, loader):

    def _wrapped(p, s):
        loader_calls['n'] += 1
        return loader(p, s)
    return real(profile, stratum, _wrapped)
cache.get = _counting_get
b = ContextualBandit(bandit_db, profile_id='inv', cache=cache)
ch1 = b.choose(_ctx(), query_id='q1')
assert loader_calls['n'] == 1
b.choose(_ctx(), query_id='q2')
assert loader_calls['n'] == 1
assert b.update(ch1.play_id, reward=1.0) is True
b.choose(_ctx(), query_id='q3')
assert loader_calls['n'] == 2
```

## Next Steps


---

*Source: test_bandit_core.py:308 | Complexity: Advanced | Last updated: 2026-05-05*