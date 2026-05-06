# How To: Settle With Unsettleable Played At Ignored

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Rows with invalid played_at ISO strings are skipped.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `time`
- `dataclasses`
- `datetime`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.learning.ensemble`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.storage.migration_runner`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Rows with invalid played_at ISO strings are skipped.'

```python
'Rows with invalid played_at ISO strings are skipped.'
```

**Verification:**
```python
assert 'M005_bandit_tables' in stats['applied']
```

### Step 2: Assign learning = value

```python
learning = tmp_path / 'learning.db'
```

**Verification:**
```python
assert n == 0
```

### Step 3: Assign memory = value

```python
memory = tmp_path / 'memory.db'
```

### Step 4: Assign stats = apply_all(...)

```python
stats = apply_all(learning, memory)
```

**Verification:**
```python
assert 'M005_bandit_tables' in stats['applied']
```

### Step 5: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(learning), isolation_level=None)
```

### Step 6: Call sqlite3.connect.close()

```python
sqlite3.connect(str(memory)).close()
```

### Step 7: Assign n = settle_stale_plays(...)

```python
n = settle_stale_plays('p', learning, memory, now=datetime.now(timezone.utc))
```

**Verification:**
```python
assert n == 0
```

### Step 8: Call conn.execute()

```python
conn.execute("INSERT INTO bandit_plays (profile_id, query_id, stratum, arm_id, played_at) VALUES ('p', 'q', 's', 'fallback_default', 'not-a-date')")
```

### Step 9: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Rows with invalid played_at ISO strings are skipped.'
learning = tmp_path / 'learning.db'
memory = tmp_path / 'memory.db'
stats = apply_all(learning, memory)
assert 'M005_bandit_tables' in stats['applied']
conn = sqlite3.connect(str(learning), isolation_level=None)
try:
    conn.execute("INSERT INTO bandit_plays (profile_id, query_id, stratum, arm_id, played_at) VALUES ('p', 'q', 's', 'fallback_default', 'not-a-date')")
finally:
    conn.close()
sqlite3.connect(str(memory)).close()
n = settle_stale_plays('p', learning, memory, now=datetime.now(timezone.utc))
assert n == 0
```

## Next Steps


---

*Source: test_bandit_supplementary.py:367 | Complexity: Advanced | Last updated: 2026-05-05*