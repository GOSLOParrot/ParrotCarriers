# How To: Scan Relabels Trigger Type

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When HealthCheck runs, candidates should have HEALTH_CHECK trigger.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `dataclasses`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.evolution.types`
- `superlocalmemory.evolution.evolution_store`
- `superlocalmemory.evolution.triggers`
- `superlocalmemory.evolution.mutation_generator`
- `superlocalmemory.evolution.blind_verifier`
- `superlocalmemory.evolution.skill_evolver`

**Setup Required:**
```python
# Fixtures: trigger_db
```

## Step-by-Step Guide

### Step 1: 'When HealthCheck runs, candidates should have HEALTH_CHECK trigger.'

```python
'When HealthCheck runs, candidates should have HEALTH_CHECK trigger.'
```

**Verification:**
```python
assert len(candidates) == 1
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(trigger_db))
```

**Verification:**
```python
assert candidates[0].trigger == TriggerType.HEALTH_CHECK
```

### Step 3: Call conn.execute()

```python
conn.execute('INSERT INTO behavioral_assertions (profile_id, category, trigger_condition, action, confidence, evidence_count) VALUES (?, ?, ?, ?, ?, ?)', ('default', 'skill_performance', 'when considering skill needs-fix', 'effective score: 20% over 10', 0.9, 10))
```

### Step 4: Call conn.commit()

```python
conn.commit()
```

### Step 5: Call conn.close()

```python
conn.close()
```

### Step 6: Assign trigger = HealthCheckTrigger(...)

```python
trigger = HealthCheckTrigger(trigger_db)
```

### Step 7: Assign _conn = sqlite3.connect(...)

```python
_conn = sqlite3.connect(str(trigger_db))
```

### Step 8: Call _conn.execute()

```python
_conn.execute("INSERT OR REPLACE INTO evolution_cycle_state (key, value, updated_at) VALUES ('health_check_cycle_count', 2, '2026-04-15T00:00:00Z')")
```

### Step 9: Call _conn.commit()

```python
_conn.commit()
```

### Step 10: Call _conn.close()

```python
_conn.close()
```

**Verification:**
```python
assert len(candidates) == 1
```

### Step 11: Assign candidates = trigger.scan(...)

```python
candidates = trigger.scan()
```


## Complete Example

```python
# Setup
# Fixtures: trigger_db

# Workflow
'When HealthCheck runs, candidates should have HEALTH_CHECK trigger.'
conn = sqlite3.connect(str(trigger_db))
conn.execute('INSERT INTO behavioral_assertions (profile_id, category, trigger_condition, action, confidence, evidence_count) VALUES (?, ?, ?, ?, ?, ?)', ('default', 'skill_performance', 'when considering skill needs-fix', 'effective score: 20% over 10', 0.9, 10))
conn.commit()
conn.close()
trigger = HealthCheckTrigger(trigger_db)
_conn = sqlite3.connect(str(trigger_db))
_conn.execute("INSERT OR REPLACE INTO evolution_cycle_state (key, value, updated_at) VALUES ('health_check_cycle_count', 2, '2026-04-15T00:00:00Z')")
_conn.commit()
_conn.close()
with patch('superlocalmemory.evolution.triggers._check_memory_pressure', return_value=False):
    candidates = trigger.scan()
assert len(candidates) == 1
assert candidates[0].trigger == TriggerType.HEALTH_CHECK
```

## Next Steps


---

*Source: test_evolution.py:802 | Complexity: Advanced | Last updated: 2026-05-05*