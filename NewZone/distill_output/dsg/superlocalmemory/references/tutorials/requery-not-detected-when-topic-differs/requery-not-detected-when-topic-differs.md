# How To: Requery Not Detected When Topic Differs

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Different topic → NOT a requery → default after 120 s.

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

### Step 1: 'Different topic → NOT a requery → default after 120 s.'

```python
'Different topic → NOT a requery → default after 120 s.'
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
play_id = _seed_play(env['learning'], 'q-other', played)
```

### Step 5: Call _seed_signals()

```python
_seed_signals(env['learning'], 'q-other', ['factY'])
```

### Step 6: Call _seed_tool_event()

```python
_seed_tool_event(env['memory'], played - timedelta(seconds=1), 'recall', {'query': 'alpha beta gamma'})
```

### Step 7: Call _seed_tool_event()

```python
_seed_tool_event(env['memory'], played + timedelta(seconds=10), 'recall', {'query': 'completely unrelated topic here'})
```

### Step 8: Assign settled = settle_stale_plays(...)

```python
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
```

**Verification:**
```python
assert settled == 1
```

### Step 9: Assign unknown = _read_play(...)

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
'Different topic → NOT a requery → default after 120 s.'
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
played = now - timedelta(seconds=200)
play_id = _seed_play(env['learning'], 'q-other', played)
_seed_signals(env['learning'], 'q-other', ['factY'])
_seed_tool_event(env['memory'], played - timedelta(seconds=1), 'recall', {'query': 'alpha beta gamma'})
_seed_tool_event(env['memory'], played + timedelta(seconds=10), 'recall', {'query': 'completely unrelated topic here'})
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
assert settled == 1
reward, kind = _read_play(env['learning'], play_id)
assert reward == pytest.approx(0.5)
assert kind == 'default'
```

## Next Steps


---

*Source: test_reward_proxy.py:256 | Complexity: Advanced | Last updated: 2026-05-05*