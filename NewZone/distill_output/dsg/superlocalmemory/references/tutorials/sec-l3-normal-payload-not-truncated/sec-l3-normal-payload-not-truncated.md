# How To: Sec L3 Normal Payload Not Truncated

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test sec l3 normal payload not truncated

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db = value

```python
db = tmp_path / 'memory.db'
```

**Verification:**
```python
assert archived == ['fact-small-1']
```

### Step 2: Call _bootstrap_schema()

```python
_bootstrap_schema(db)
```

**Verification:**
```python
assert payload.get('truncated') is not True
```

### Step 3: Call _seed_fact()

```python
_seed_fact(db, 'fact-small-1', content='hello world')
```

**Verification:**
```python
assert payload['content'] == 'hello world'
```

### Step 4: Assign archived = ra.run_reward_gated_archive(...)

```python
archived = ra.run_reward_gated_archive(db, 'default', candidate_fact_ids=['fact-small-1'])
```

**Verification:**
```python
assert row['reason'] == 'reward_gated_ebbinghaus'
```

### Step 5: Assign payload = json.loads(...)

```python
payload = json.loads(row['payload_json'])
```

**Verification:**
```python
assert payload.get('truncated') is not True
```

### Step 6: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 7: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT payload_json, reason FROM memory_archive WHERE fact_id=?', ('fact-small-1',)).fetchone()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = tmp_path / 'memory.db'
_bootstrap_schema(db)
_seed_fact(db, 'fact-small-1', content='hello world')
archived = ra.run_reward_gated_archive(db, 'default', candidate_fact_ids=['fact-small-1'])
assert archived == ['fact-small-1']
with sqlite3.connect(db) as conn:
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT payload_json, reason FROM memory_archive WHERE fact_id=?', ('fact-small-1',)).fetchone()
payload = json.loads(row['payload_json'])
assert payload.get('truncated') is not True
assert payload['content'] == 'hello world'
assert row['reason'] == 'reward_gated_ebbinghaus'
```

## Next Steps


---

*Source: test_stage8_reward_archive_payload_cap.py:104 | Complexity: Intermediate | Last updated: 2026-05-05*