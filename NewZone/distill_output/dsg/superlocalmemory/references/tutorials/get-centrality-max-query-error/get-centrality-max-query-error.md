# How To: Get Centrality Max Query Error

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: get_centrality_for_fact handles max-query failure gracefully.

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

### Step 1: 'get_centrality_for_fact handles max-query failure gracefully.'

```python
'get_centrality_for_fact handles max-query failure gracefully.'
```

**Verification:**
```python
assert result == 0.0
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('f1', 'p1', 0.5, 0.5)")
```

### Step 4: Call conn.commit()

```python
conn.commit()
```

### Step 5: Assign config = SAGQConfig(...)

```python
config = SAGQConfig()
```

### Step 6: Assign call_count = value

```python
call_count = [0]
```

### Step 7: Assign original_execute = value

```python
original_execute = test_db.execute.side_effect
```

### Step 8: Assign test_db.execute.side_effect = _failing_max_execute

```python
test_db.execute.side_effect = _failing_max_execute
```

### Step 9: Assign q = ActivationGuidedQuantizer(...)

```python
q = ActivationGuidedQuantizer(test_db, config)
```

### Step 10: Assign result = q.get_centrality_for_fact(...)

```python
result = q.get_centrality_for_fact('f1', 'p1')
```

**Verification:**
```python
assert result == 0.0
```


## Complete Example

```python
# Setup
# Fixtures: test_db

# Workflow
'get_centrality_for_fact handles max-query failure gracefully.'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('f1', 'p1', 0.5, 0.5)")
conn.commit()
config = SAGQConfig()
call_count = [0]
original_execute = test_db.execute.side_effect

def _failing_max_execute(sql, params=()):
    call_count[0] += 1
    if 'MAX(pagerank_score)' in sql:
        raise RuntimeError('max query broken')
    return original_execute(sql, params)
test_db.execute.side_effect = _failing_max_execute
q = ActivationGuidedQuantizer(test_db, config)
result = q.get_centrality_for_fact('f1', 'p1')
assert result == 0.0
```

## Next Steps


---

*Source: test_sagq.py:672 | Complexity: Advanced | Last updated: 2026-05-05*