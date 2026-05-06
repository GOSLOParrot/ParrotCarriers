# How To: Sec L3 Large Payload Truncated To Stub

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test sec l3 large payload truncated to stub

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
assert archived == ['fact-huge-1']
```

### Step 2: Call _bootstrap_schema()

```python
_bootstrap_schema(db)
```

**Verification:**
```python
assert row is not None
```

### Step 3: Assign huge = value

```python
huge = 'x' * (ra.PAYLOAD_JSON_MAX_BYTES + 1024)
```

**Verification:**
```python
assert payload.get('truncated') is True
```

### Step 4: Call _seed_fact()

```python
_seed_fact(db, 'fact-huge-1', content=huge)
```

**Verification:**
```python
assert payload.get('fact_id') == 'fact-huge-1'
```

### Step 5: Assign archived = ra.run_reward_gated_archive(...)

```python
archived = ra.run_reward_gated_archive(db, 'default', candidate_fact_ids=['fact-huge-1'])
```

**Verification:**
```python
assert row['reason'] == 'reward_gated_ebbinghaus_truncated'
```

### Step 6: Assign payload = json.loads(...)

```python
payload = json.loads(row['payload_json'])
```

**Verification:**
```python
assert len(row['payload_json'].encode('utf-8')) < ra.PAYLOAD_JSON_MAX_BYTES
```

### Step 7: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 8: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT payload_json, reason FROM memory_archive WHERE fact_id=?', ('fact-huge-1',)).fetchone()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = tmp_path / 'memory.db'
_bootstrap_schema(db)
huge = 'x' * (ra.PAYLOAD_JSON_MAX_BYTES + 1024)
_seed_fact(db, 'fact-huge-1', content=huge)
archived = ra.run_reward_gated_archive(db, 'default', candidate_fact_ids=['fact-huge-1'])
assert archived == ['fact-huge-1']
with sqlite3.connect(db) as conn:
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT payload_json, reason FROM memory_archive WHERE fact_id=?', ('fact-huge-1',)).fetchone()
assert row is not None
payload = json.loads(row['payload_json'])
assert payload.get('truncated') is True
assert payload.get('fact_id') == 'fact-huge-1'
assert row['reason'] == 'reward_gated_ebbinghaus_truncated'
assert len(row['payload_json'].encode('utf-8')) < ra.PAYLOAD_JSON_MAX_BYTES
```

## Next Steps


---

*Source: test_stage8_reward_archive_payload_cap.py:74 | Complexity: Advanced | Last updated: 2026-05-05*