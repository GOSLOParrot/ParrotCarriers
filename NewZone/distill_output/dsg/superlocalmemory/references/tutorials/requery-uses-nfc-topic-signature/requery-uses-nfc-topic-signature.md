# How To: Requery Uses Nfc Topic Signature

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: A follow-up query with equivalent NFC form triggers proxy_requery.

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

### Step 1: 'A follow-up query with equivalent NFC form triggers proxy_requery.'

```python
'A follow-up query with equivalent NFC form triggers proxy_requery.'
```

**Verification:**
```python
assert compute_topic_signature(original) == compute_topic_signature(requery)
```

### Step 2: Assign now = datetime(...)

```python
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
```

**Verification:**
```python
assert settled == 1
```

### Step 3: Assign played = value

```python
played = now - timedelta(seconds=90)
```

**Verification:**
```python
assert reward == pytest.approx(0.0)
```

### Step 4: Assign play_id = _seed_play(...)

```python
play_id = _seed_play(env['learning'], 'q-req', played)
```

**Verification:**
```python
assert kind == 'proxy_requery'
```

### Step 5: Call _seed_signals()

```python
_seed_signals(env['learning'], 'q-req', ['factX'])
```

### Step 6: Assign original = 'café latté order'

```python
original = 'café latté order'
```

### Step 7: Assign requery = unicodedata.normalize(...)

```python
requery = unicodedata.normalize('NFD', 'café latté order')
```

**Verification:**
```python
assert compute_topic_signature(original) == compute_topic_signature(requery)
```

### Step 8: Call _seed_tool_event()

```python
_seed_tool_event(env['memory'], played - timedelta(seconds=1), 'recall', {'query': original})
```

### Step 9: Call _seed_tool_event()

```python
_seed_tool_event(env['memory'], played + timedelta(seconds=10), 'recall', {'query': requery})
```

### Step 10: Assign settled = settle_stale_plays(...)

```python
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
```

**Verification:**
```python
assert settled == 1
```

### Step 11: Assign unknown = _read_play(...)

```python
reward, kind = _read_play(env['learning'], play_id)
```

**Verification:**
```python
assert reward == pytest.approx(0.0)
```


## Complete Example

```python
# Setup
# Fixtures: env

# Workflow
'A follow-up query with equivalent NFC form triggers proxy_requery.'
now = datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc)
played = now - timedelta(seconds=90)
play_id = _seed_play(env['learning'], 'q-req', played)
_seed_signals(env['learning'], 'q-req', ['factX'])
original = 'café latté order'
requery = unicodedata.normalize('NFD', 'café latté order')
assert compute_topic_signature(original) == compute_topic_signature(requery)
_seed_tool_event(env['memory'], played - timedelta(seconds=1), 'recall', {'query': original})
_seed_tool_event(env['memory'], played + timedelta(seconds=10), 'recall', {'query': requery})
settled = settle_stale_plays(PROFILE, env['learning'], env['memory'], now=now, bandit=env['bandit'])
assert settled == 1
reward, kind = _read_play(env['learning'], play_id)
assert reward == pytest.approx(0.0)
assert kind == 'proxy_requery'
```

## Next Steps


---

*Source: test_reward_proxy.py:222 | Complexity: Advanced | Last updated: 2026-05-05*