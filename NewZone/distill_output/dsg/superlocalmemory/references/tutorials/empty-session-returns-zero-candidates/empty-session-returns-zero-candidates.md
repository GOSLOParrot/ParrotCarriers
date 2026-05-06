# How To: Empty Session Returns Zero Candidates

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test empty session returns zero candidates

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db_path = value

```python
db_path = tmp_path / 'test.db'
```

**Verification:**
```python
assert result['candidates'] == 0
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

**Verification:**
```python
assert result['evolved'] == 0
```

### Step 3: Call conn.execute()

```python
conn.execute('CREATE TABLE IF NOT EXISTS tool_events (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, profile_id TEXT, tool_name TEXT, input_summary TEXT, output_summary TEXT, created_at TEXT)')
```

### Step 4: Call conn.commit()

```python
conn.commit()
```

### Step 5: Call conn.close()

```python
conn.close()
```

### Step 6: Assign evolver = SkillEvolver(...)

```python
evolver = SkillEvolver(db_path)
```

**Verification:**
```python
assert result['candidates'] == 0
```

### Step 7: Assign result = evolver.run_post_session(...)

```python
result = evolver.run_post_session('nonexistent-session')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db_path = tmp_path / 'test.db'
conn = sqlite3.connect(str(db_path))
conn.execute('CREATE TABLE IF NOT EXISTS tool_events (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, profile_id TEXT, tool_name TEXT, input_summary TEXT, output_summary TEXT, created_at TEXT)')
conn.commit()
conn.close()
evolver = SkillEvolver(db_path)
with patch('superlocalmemory.evolution.triggers._check_memory_pressure', return_value=False):
    result = evolver.run_post_session('nonexistent-session')
assert result['candidates'] == 0
assert result['evolved'] == 0
```

## Next Steps


---

*Source: test_evolution.py:1279 | Complexity: Intermediate | Last updated: 2026-05-05*