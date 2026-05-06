# How To: Skill With Negative Signals Becomes Fix Candidate

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test skill with negative signals becomes fix candidate

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

### Step 1: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(trigger_db))
```

**Verification:**
```python
assert len(candidates) >= 1
```

### Step 2: Call conn.commit()

```python
conn.commit()
```

**Verification:**
```python
assert c.skill_name == 'bad-skill'
```

### Step 3: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert c.evolution_type == EvolutionType.FIX
```

### Step 4: Assign trigger = PostSessionTrigger(...)

```python
trigger = PostSessionTrigger(trigger_db)
```

**Verification:**
```python
assert c.trigger == TriggerType.POST_SESSION
```

### Step 5: Assign c = value

```python
c = candidates[0]
```

**Verification:**
```python
assert c.skill_name == 'bad-skill'
```

### Step 6: Call conn.execute()

```python
conn.execute('INSERT INTO tool_events (session_id, profile_id, tool_name, input_summary, output_summary, created_at) VALUES (?, ?, ?, ?, ?, ?)', ('sess-1', 'default', 'Skill', json.dumps({'skill': 'bad-skill'}), '', f'2026-04-15T00:0{invoc}:00Z'))
```

### Step 7: Assign candidates = trigger.scan(...)

```python
candidates = trigger.scan('sess-1')
```

### Step 8: Call conn.execute()

```python
conn.execute('INSERT INTO tool_events (session_id, profile_id, tool_name, input_summary, output_summary, created_at) VALUES (?, ?, ?, ?, ?, ?)', ('sess-1', 'default', 'Bash', '', 'error: command failed', f'2026-04-15T00:0{invoc}:01Z'))
```


## Complete Example

```python
# Setup
# Fixtures: trigger_db

# Workflow
conn = sqlite3.connect(str(trigger_db))
for invoc in range(5):
    conn.execute('INSERT INTO tool_events (session_id, profile_id, tool_name, input_summary, output_summary, created_at) VALUES (?, ?, ?, ?, ?, ?)', ('sess-1', 'default', 'Skill', json.dumps({'skill': 'bad-skill'}), '', f'2026-04-15T00:0{invoc}:00Z'))
    if invoc < NEGATIVE_SIGNALS_THRESHOLD:
        conn.execute('INSERT INTO tool_events (session_id, profile_id, tool_name, input_summary, output_summary, created_at) VALUES (?, ?, ?, ?, ?, ?)', ('sess-1', 'default', 'Bash', '', 'error: command failed', f'2026-04-15T00:0{invoc}:01Z'))
conn.commit()
conn.close()
trigger = PostSessionTrigger(trigger_db)
with patch('superlocalmemory.evolution.triggers._check_memory_pressure', return_value=False):
    candidates = trigger.scan('sess-1')
assert len(candidates) >= 1
c = candidates[0]
assert c.skill_name == 'bad-skill'
assert c.evolution_type == EvolutionType.FIX
assert c.trigger == TriggerType.POST_SESSION
```

## Next Steps


---

*Source: test_evolution.py:626 | Complexity: Advanced | Last updated: 2026-05-05*