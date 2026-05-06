# How To: Archive Never Deletes From Atomic Facts

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: LLD-12 §1 — archive must UPDATE status, not DELETE row.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`

**Setup Required:**
```python
# Fixtures: mem_db
```

## Step-by-Step Guide

### Step 1: 'LLD-12 §1 — archive must UPDATE status, not DELETE row.'

```python
'LLD-12 §1 — archive must UPDATE status, not DELETE row.'
```

**Verification:**
```python
assert row is not None, 'row must still exist (never deleted)'
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(mem_db)
```

**Verification:**
```python
assert row[0] == 'archived'
```

### Step 3: Call conn.set_authorizer()

```python
conn.set_authorizer(_authorizer)
```

**Verification:**
```python
assert row[1]
```

### Step 4: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert archive_row == 1
```

### Step 5: Call run_reward_gated_archive()

```python
run_reward_gated_archive(mem_db, 'p1', candidate_fact_ids=['cold'])
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(mem_db)
```

### Step 7: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute("SELECT archive_status, archive_reason FROM atomic_facts WHERE fact_id='cold'").fetchone()
```

### Step 8: Assign archive_row = value

```python
archive_row = conn.execute("SELECT COUNT(*) FROM memory_archive WHERE fact_id='cold'").fetchone()[0]
```

### Step 9: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert row is not None, 'row must still exist (never deleted)'
```

### Step 10: Call conn.execute()

```python
conn.execute("INSERT INTO atomic_facts (fact_id, profile_id, content) VALUES ('cold', 'p1', 'stale fact')")
```


## Complete Example

```python
# Setup
# Fixtures: mem_db

# Workflow
'LLD-12 §1 — archive must UPDATE status, not DELETE row.'
from superlocalmemory.learning.hnsw_dedup import run_reward_gated_archive
with sqlite3.connect(mem_db) as conn:
    conn.execute("INSERT INTO atomic_facts (fact_id, profile_id, content) VALUES ('cold', 'p1', 'stale fact')")
conn = sqlite3.connect(mem_db)

def _authorizer(code, arg1, arg2, arg3, arg4):
    if code == sqlite3.SQLITE_DELETE and arg1 == 'atomic_facts':
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK
conn.set_authorizer(_authorizer)
conn.close()
run_reward_gated_archive(mem_db, 'p1', candidate_fact_ids=['cold'])
conn = sqlite3.connect(mem_db)
row = conn.execute("SELECT archive_status, archive_reason FROM atomic_facts WHERE fact_id='cold'").fetchone()
archive_row = conn.execute("SELECT COUNT(*) FROM memory_archive WHERE fact_id='cold'").fetchone()[0]
conn.close()
assert row is not None, 'row must still exist (never deleted)'
assert row[0] == 'archived'
assert row[1]
assert archive_row == 1
```

## Next Steps


---

*Source: test_reward_gated_archive.py:67 | Complexity: Advanced | Last updated: 2026-05-05*