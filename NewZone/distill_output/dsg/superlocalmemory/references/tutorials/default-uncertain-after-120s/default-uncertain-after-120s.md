# How To: Default Uncertain After 120S

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: No hit, no requery, > 120 s → reward=0.5, kind=default.

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

### Step 1: 'No hit, no requery, > 120 s → reward=0.5, kind=default.'

```python
'No hit, no requery, > 120 s → reward=0.5, kind=default.'
```

**Verification:**
```python
assert settled == 1
```

### Step 2: Assign now = datetime(...)

```python
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
```

**Verification:**
```python
assert reward == pytest.approx(0.5)
```

### Step 3: Assign played = value

```python
played = now - timedelta(seconds=200)
```

**Verification:**
```python
assert kind == 'default'
```

### Step 4: Assign play_id = _seed_play(...)

```python
play_id = _seed_play(env['learning'], 'q-default', played)
```

### Step 5: Call _seed_signals()

```python
_seed_signals(env['learning'], 'q-default', ['f1'])
```

### Step 6: Assign settled = settle_stale_plays(...)

```python
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
```

**Verification:**
```python
assert settled == 1
```

### Step 7: Assign unknown = _read_play(...)

```python
reward, kind = _read_play(env['learning'], play_id)
```

**Verification:**
```python
assert reward == pytest.approx(0.5)
```


## Complete Example

```python
# Setup
# Fixtures: env

# Workflow
'No hit, no requery, > 120 s → reward=0.5, kind=default.'
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
played = now - timedelta(seconds=200)
play_id = _seed_play(env['learning'], 'q-default', played)
_seed_signals(env['learning'], 'q-default', ['f1'])
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
assert settled == 1
reward, kind = _read_play(env['learning'], play_id)
assert reward == pytest.approx(0.5)
assert kind == 'default'
```

## Next Steps


---

*Source: test_reward_proxy.py:186 | Complexity: Intermediate | Last updated: 2026-05-05*