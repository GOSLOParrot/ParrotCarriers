# How To: Proxy Position Hit

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Tool event references a top-3 fact within 30 s → reward=1.0.

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

### Step 1: 'Tool event references a top-3 fact within 30 s → reward=1.0.'

```python
'Tool event references a top-3 fact within 30 s → reward=1.0.'
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
assert reward == pytest.approx(1.0)
```

### Step 3: Assign played = value

```python
played = now - timedelta(seconds=90)
```

**Verification:**
```python
assert kind == 'proxy_position'
```

### Step 4: Assign play_id = _seed_play(...)

```python
play_id = _seed_play(env['learning'], 'q1', played)
```

### Step 5: Call _seed_signals()

```python
_seed_signals(env['learning'], 'q1', ['factA', 'factB', 'factC'])
```

### Step 6: Call _seed_tool_event()

```python
_seed_tool_event(env['memory'], played + timedelta(seconds=15), 'Read', {'path': '/home/foo/factB.md'})
```

### Step 7: Assign settled = settle_stale_plays(...)

```python
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
```

**Verification:**
```python
assert settled == 1
```

### Step 8: Assign unknown = _read_play(...)

```python
reward, kind = _read_play(env['learning'], play_id)
```

**Verification:**
```python
assert reward == pytest.approx(1.0)
```


## Complete Example

```python
# Setup
# Fixtures: env

# Workflow
'Tool event references a top-3 fact within 30 s → reward=1.0.'
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
played = now - timedelta(seconds=90)
play_id = _seed_play(env['learning'], 'q1', played)
_seed_signals(env['learning'], 'q1', ['factA', 'factB', 'factC'])
_seed_tool_event(env['memory'], played + timedelta(seconds=15), 'Read', {'path': '/home/foo/factB.md'})
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
assert settled == 1
reward, kind = _read_play(env['learning'], play_id)
assert reward == pytest.approx(1.0)
assert kind == 'proxy_position'
```

## Next Steps


---

*Source: test_reward_proxy.py:150 | Complexity: Advanced | Last updated: 2026-05-05*