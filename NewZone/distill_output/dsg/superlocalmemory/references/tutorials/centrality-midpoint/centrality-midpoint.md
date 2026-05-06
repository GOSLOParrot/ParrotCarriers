# How To: Centrality Midpoint

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Two facts: one at max, one at half should give centrality ~0.5.

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
# Fixtures: quantizer, test_db
```

## Step-by-Step Guide

### Step 1: 'Two facts: one at max, one at half should give centrality ~0.5.'

```python
'Two facts: one at max, one at half should give centrality ~0.5.'
```

**Verification:**
```python
assert hub.combined_centrality == pytest.approx(1.0, abs=1e-06)
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

**Verification:**
```python
assert mid.combined_centrality == pytest.approx(0.5, abs=1e-06)
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('hub', 'p1', 1.0, 1.0)")
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('mid', 'p1', 0.5, 0.5)")
```

### Step 5: Call conn.execute()

```python
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c1', 'p1', 'q1', 'hub', 0.9, 3, datetime('now'))")
```

### Step 6: Call conn.execute()

```python
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c2', 'p1', 'q2', 'hub', 0.8, 3, datetime('now'))")
```

### Step 7: Call conn.execute()

```python
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c3', 'p1', 'q3', 'mid', 0.5, 3, datetime('now'))")
```

### Step 8: Call conn.commit()

```python
conn.commit()
```

### Step 9: Assign result = quantizer.compute_centrality_batch(...)

```python
result = quantizer.compute_centrality_batch('p1')
```

### Step 10: Assign by_id = value

```python
by_id = {cs.fact_id: cs for cs in result}
```

### Step 11: Assign hub = value

```python
hub = by_id['hub']
```

**Verification:**
```python
assert hub.combined_centrality == pytest.approx(1.0, abs=1e-06)
```

### Step 12: Assign mid = value

```python
mid = by_id['mid']
```

**Verification:**
```python
assert mid.combined_centrality == pytest.approx(0.5, abs=1e-06)
```


## Complete Example

```python
# Setup
# Fixtures: quantizer, test_db

# Workflow
'Two facts: one at max, one at half should give centrality ~0.5.'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('hub', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('mid', 'p1', 0.5, 0.5)")
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c1', 'p1', 'q1', 'hub', 0.9, 3, datetime('now'))")
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c2', 'p1', 'q2', 'hub', 0.8, 3, datetime('now'))")
conn.execute("INSERT INTO activation_cache (cache_id, profile_id, query_hash, node_id, activation_value, iteration, created_at) VALUES ('c3', 'p1', 'q3', 'mid', 0.5, 3, datetime('now'))")
conn.commit()
result = quantizer.compute_centrality_batch('p1')
by_id = {cs.fact_id: cs for cs in result}
hub = by_id['hub']
assert hub.combined_centrality == pytest.approx(1.0, abs=1e-06)
mid = by_id['mid']
assert mid.combined_centrality == pytest.approx(0.5, abs=1e-06)
```

## Next Steps


---

*Source: test_sagq.py:155 | Complexity: Advanced | Last updated: 2026-05-05*