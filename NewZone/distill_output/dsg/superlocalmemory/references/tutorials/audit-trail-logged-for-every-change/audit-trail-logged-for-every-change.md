# How To: Audit Trail Logged For Every Change

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: After run with changes, fact_access_log has entries with access_type='consolidation'.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `datetime`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.dynamics.activation_guided_quantization`
- `superlocalmemory.learning.quantization_scheduler`
- `json`

**Setup Required:**
```python
# Fixtures: scheduler, test_db
```

## Step-by-Step Guide

### Step 1: "After run with changes, fact_access_log has entries with access_type='consolidation'."

```python
"After run with changes, fact_access_log has entries with access_type='consolidation'."
```

**Verification:**
```python
assert len(audit_rows) == change_count
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

**Verification:**
```python
assert change_count >= 1
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('ref', 'p1', 1.0, 1.0)")
```

**Verification:**
```python
assert d['session_id'] == 'sagq_scheduler'
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('ref', 'p1', 32)")
```

**Verification:**
```python
assert d['access_type'] == 'consolidation'
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Assign scheduler._eap_mapper = value

```python
scheduler._eap_mapper = lambda fid: 2 if fid.startswith('audit') else 32
```

### Step 7: Assign result = scheduler.run(...)

```python
result = scheduler.run('p1')
```

### Step 8: Assign audit_rows = conn.execute.fetchall(...)

```python
audit_rows = conn.execute("SELECT * FROM fact_access_log WHERE access_type = 'consolidation'").fetchall()
```

### Step 9: Assign change_count = value

```python
change_count = result.downgrades + result.upgrades
```

**Verification:**
```python
assert len(audit_rows) == change_count
```

### Step 10: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES (?, 'p1', 0.0, 0.0)", (f'audit{i}',))
```

### Step 11: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES (?, 'p1', 32)", (f'audit{i}',))
```

### Step 12: Assign d = dict(...)

```python
d = dict(row)
```

**Verification:**
```python
assert d['session_id'] == 'sagq_scheduler'
```


## Complete Example

```python
# Setup
# Fixtures: scheduler, test_db

# Workflow
"After run with changes, fact_access_log has entries with access_type='consolidation'."
conn = test_db._test_conn
for i in range(3):
    conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES (?, 'p1', 0.0, 0.0)", (f'audit{i}',))
    conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES (?, 'p1', 32)", (f'audit{i}',))
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('ref', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('ref', 'p1', 32)")
conn.commit()
scheduler._eap_mapper = lambda fid: 2 if fid.startswith('audit') else 32
result = scheduler.run('p1')
audit_rows = conn.execute("SELECT * FROM fact_access_log WHERE access_type = 'consolidation'").fetchall()
change_count = result.downgrades + result.upgrades
assert len(audit_rows) == change_count
assert change_count >= 1
for row in audit_rows:
    d = dict(row)
    assert d['session_id'] == 'sagq_scheduler'
    assert d['access_type'] == 'consolidation'
```

## Next Steps


---

*Source: test_quant_scheduler.py:369 | Complexity: Advanced | Last updated: 2026-05-05*