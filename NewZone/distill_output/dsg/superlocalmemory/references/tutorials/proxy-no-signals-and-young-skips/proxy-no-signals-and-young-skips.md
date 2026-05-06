# How To: Proxy No Signals And Young Skips

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: < 60 s old → not yet settleable.

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
# Fixtures: env
```

## Step-by-Step Guide

### Step 1: '< 60 s old → not yet settleable.'

```python
'< 60 s old → not yet settleable.'
```

**Verification:**
```python
assert settled == 0
```

### Step 2: Assign now = datetime(...)

```python
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
```

**Verification:**
```python
assert reward is None
```

### Step 3: Assign played = value

```python
played = now - timedelta(seconds=30)
```

**Verification:**
```python
assert kind is None
```

### Step 4: Assign play_id = _seed_play(...)

```python
play_id = _seed_play(env['learning'], 'q-young', played)
```

### Step 5: Assign settled = settle_stale_plays(...)

```python
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
```

**Verification:**
```python
assert settled == 0
```

### Step 6: Assign unknown = _read_play(...)

```python
reward, kind = _read_play(env['learning'], play_id)
```

**Verification:**
```python
assert reward is None
```


## Complete Example

```python
# Setup
# Fixtures: env

# Workflow
'< 60 s old → not yet settleable.'
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
played = now - timedelta(seconds=30)
play_id = _seed_play(env['learning'], 'q-young', played)
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
assert settled == 0
reward, kind = _read_play(env['learning'], play_id)
assert reward is None
assert kind is None
```

## Next Steps


---

*Source: test_reward_proxy.py:171 | Complexity: Intermediate | Last updated: 2026-05-05*