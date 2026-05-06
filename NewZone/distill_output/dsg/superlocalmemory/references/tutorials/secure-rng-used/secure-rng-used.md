# How To: Secure Rng Used

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: B1: choose() must call into secrets.SystemRandom().betavariate.

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
# Fixtures: bandit_db, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'B1: choose() must call into secrets.SystemRandom().betavariate.'

```python
'B1: choose() must call into secrets.SystemRandom().betavariate.'
```

**Verification:**
```python
assert call_counter['n'] >= 40
```

### Step 2: Assign call_counter = value

```python
call_counter = {'n': 0}
```

### Step 3: Assign real_system_random = value

```python
real_system_random = _secrets.SystemRandom
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.learning.bandit.secrets.SystemRandom', _Spy)
```

### Step 5: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(bandit_db, profile_id='rng', cache=_BanditCache(max_entries=8))
```

### Step 6: Call b.choose()

```python
b.choose(_ctx(), query_id='rng-q')
```

**Verification:**
```python
assert call_counter['n'] >= 40
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db, monkeypatch

# Workflow
'B1: choose() must call into secrets.SystemRandom().betavariate.'
call_counter = {'n': 0}
real_system_random = _secrets.SystemRandom

class _Spy(real_system_random):

    def betavariate(self, a, b):
        call_counter['n'] += 1
        return super().betavariate(a, b)
monkeypatch.setattr('superlocalmemory.learning.bandit.secrets.SystemRandom', _Spy)
b = ContextualBandit(bandit_db, profile_id='rng', cache=_BanditCache(max_entries=8))
b.choose(_ctx(), query_id='rng-q')
assert call_counter['n'] >= 40
```

## Next Steps


---

*Source: test_bandit_core.py:253 | Complexity: Intermediate | Last updated: 2026-05-05*