# How To: On Access Strengthens

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: After on_access_event, retention increases or stays same.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `time`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.learning.forgetting_scheduler`
- `superlocalmemory.math.ebbinghaus`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage`
- `superlocalmemory.storage.schema_v32`
- `superlocalmemory.storage`
- `superlocalmemory.storage.schema_v32`

**Setup Required:**
```python
# Fixtures: db_with_facts, ebbinghaus, config
```

## Step-by-Step Guide

### Step 1: 'After on_access_event, retention increases or stays same.'

```python
'After on_access_event, retention increases or stays same.'
```

**Verification:**
```python
assert len(initial) > 0, 'fact_000 should have retention data'
```

### Step 2: Assign scheduler = ForgettingScheduler(...)

```python
scheduler = ForgettingScheduler(db_with_facts, ebbinghaus, config)
```

**Verification:**
```python
assert updated_strength >= initial_strength, f'Strength should increase after access: was {initial_strength}, now {updated_strength}'
```

### Step 3: Call scheduler.run_decay_cycle()

```python
scheduler.run_decay_cycle('test_profile')
```

### Step 4: Assign initial = db_with_facts.execute(...)

```python
initial = db_with_facts.execute('SELECT retention_score, memory_strength FROM fact_retention WHERE fact_id = ? AND profile_id = ?', ('fact_000', 'test_profile'))
```

**Verification:**
```python
assert len(initial) > 0, 'fact_000 should have retention data'
```

### Step 5: Assign initial_strength = float(...)

```python
initial_strength = float(dict(initial[0])['memory_strength'])
```

### Step 6: Call scheduler.on_access_event()

```python
scheduler.on_access_event('fact_000', 'test_profile')
```

### Step 7: Assign updated = db_with_facts.execute(...)

```python
updated = db_with_facts.execute('SELECT retention_score, memory_strength FROM fact_retention WHERE fact_id = ? AND profile_id = ?', ('fact_000', 'test_profile'))
```

### Step 8: Assign updated_strength = float(...)

```python
updated_strength = float(dict(updated[0])['memory_strength'])
```

**Verification:**
```python
assert updated_strength >= initial_strength, f'Strength should increase after access: was {initial_strength}, now {updated_strength}'
```


## Complete Example

```python
# Setup
# Fixtures: db_with_facts, ebbinghaus, config

# Workflow
'After on_access_event, retention increases or stays same.'
scheduler = ForgettingScheduler(db_with_facts, ebbinghaus, config)
scheduler.run_decay_cycle('test_profile')
initial = db_with_facts.execute('SELECT retention_score, memory_strength FROM fact_retention WHERE fact_id = ? AND profile_id = ?', ('fact_000', 'test_profile'))
assert len(initial) > 0, 'fact_000 should have retention data'
initial_strength = float(dict(initial[0])['memory_strength'])
scheduler.on_access_event('fact_000', 'test_profile')
updated = db_with_facts.execute('SELECT retention_score, memory_strength FROM fact_retention WHERE fact_id = ? AND profile_id = ?', ('fact_000', 'test_profile'))
updated_strength = float(dict(updated[0])['memory_strength'])
assert updated_strength >= initial_strength, f'Strength should increase after access: was {initial_strength}, now {updated_strength}'
```

## Next Steps


---

*Source: test_forgetting_scheduler.py:134 | Complexity: Advanced | Last updated: 2026-05-05*