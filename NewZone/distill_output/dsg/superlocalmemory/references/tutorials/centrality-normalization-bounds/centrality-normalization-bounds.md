# How To: Centrality Normalization Bounds

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: All centrality scores must be in [0.0, 1.0].

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

### Step 1: 'All centrality scores must be in [0.0, 1.0].'

```python
'All centrality scores must be in [0.0, 1.0].'
```

**Verification:**
```python
assert len(result) == 20
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

**Verification:**
```python
assert 0.0 <= cs.combined_centrality <= 1.0
```

### Step 3: Call conn.commit()

```python
conn.commit()
```

**Verification:**
```python
assert 0.0 <= cs.pagerank_norm <= 1.0
```

### Step 4: Assign result = quantizer.compute_centrality_batch(...)

```python
result = quantizer.compute_centrality_batch('p1')
```

**Verification:**
```python
assert 0.0 <= cs.degree_norm <= 1.0
```

### Step 5: Assign pr = value

```python
pr = i * 0.05
```

**Verification:**
```python
assert 0.0 <= cs.sa_freq_norm <= 1.0
```

### Step 6: Assign deg = value

```python
deg = (20 - i) * 0.05
```

### Step 7: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES (?, 'p1', ?, ?)", (f'f{i}', pr, deg))
```

**Verification:**
```python
assert 0.0 <= cs.combined_centrality <= 1.0
```


## Complete Example

```python
# Setup
# Fixtures: quantizer, test_db

# Workflow
'All centrality scores must be in [0.0, 1.0].'
conn = test_db._test_conn
for i in range(20):
    pr = i * 0.05
    deg = (20 - i) * 0.05
    conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES (?, 'p1', ?, ?)", (f'f{i}', pr, deg))
conn.commit()
result = quantizer.compute_centrality_batch('p1')
assert len(result) == 20
for cs in result:
    assert 0.0 <= cs.combined_centrality <= 1.0
    assert 0.0 <= cs.pagerank_norm <= 1.0
    assert 0.0 <= cs.degree_norm <= 1.0
    assert 0.0 <= cs.sa_freq_norm <= 1.0
```

## Next Steps


---

*Source: test_sagq.py:204 | Complexity: Intermediate | Last updated: 2026-05-05*