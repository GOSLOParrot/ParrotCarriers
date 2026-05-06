# How To: Get Centrality Sa Max Subquery Error

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: get_centrality_for_fact handles SA max subquery failure (line 370-371).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.dynamics.activation_guided_quantization`
- `math`

**Setup Required:**
```python
# Fixtures: test_db
```

## Step-by-Step Guide

### Step 1: 'get_centrality_for_fact handles SA max subquery failure (line 370-371).'

```python
'get_centrality_for_fact handles SA max subquery failure (line 370-371).'
```

**Verification:**
```python
assert 0.0 <= result <= 1.0
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('f1', 'p1', 0.5, 0.5)")
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c1', 'p1', 'q1', 'f1', 0.5, 3, datetime('now'))")
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Assign config = SAGQConfig(...)

```python
config = SAGQConfig()
```

### Step 7: Assign original_execute = value

```python
original_execute = test_db.execute.side_effect
```

### Step 8: Assign call_count = value

```python
call_count = [0]
```

### Step 9: Assign test_db.execute.side_effect = _failing_sa_max

```python
test_db.execute.side_effect = _failing_sa_max
```

### Step 10: Assign q = ActivationGuidedQuantizer(...)

```python
q = ActivationGuidedQuantizer(test_db, config)
```

### Step 11: Assign result = q.get_centrality_for_fact(...)

```python
result = q.get_centrality_for_fact('f1', 'p1')
```

**Verification:**
```python
assert 0.0 <= result <= 1.0
```


## Complete Example

```python
# Setup
# Fixtures: test_db

# Workflow
'get_centrality_for_fact handles SA max subquery failure (line 370-371).'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('f1', 'p1', 0.5, 0.5)")
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c1', 'p1', 'q1', 'f1', 0.5, 3, datetime('now'))")
conn.commit()
config = SAGQConfig()
original_execute = test_db.execute.side_effect
call_count = [0]

def _failing_sa_max(sql, params=()):
    call_count[0] += 1
    if 'MAX(cnt)' in sql:
        raise RuntimeError('sa max query broken')
    return original_execute(sql, params)
test_db.execute.side_effect = _failing_sa_max
q = ActivationGuidedQuantizer(test_db, config)
result = q.get_centrality_for_fact('f1', 'p1')
assert 0.0 <= result <= 1.0
```

## Next Steps


---

*Source: test_sagq.py:788 | Complexity: Advanced | Last updated: 2026-05-05*