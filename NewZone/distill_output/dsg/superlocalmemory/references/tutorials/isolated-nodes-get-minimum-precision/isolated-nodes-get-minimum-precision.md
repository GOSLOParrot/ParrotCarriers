# How To: Isolated Nodes Get Minimum Precision

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Fact with no edges (pr=0, deg=0, sa=0) -> centrality=0.0 -> sagq_bw=2.

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
# Fixtures: test_db, sagq_config
```

## Step-by-Step Guide

### Step 1: 'Fact with no edges (pr=0, deg=0, sa=0) -> centrality=0.0 -> sagq_bw=2.'

```python
'Fact with no edges (pr=0, deg=0, sa=0) -> centrality=0.0 -> sagq_bw=2.'
```

**Verification:**
```python
assert by_id['isolated'].sagq_bit_width == 2
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

**Verification:**
```python
assert by_id['isolated'].centrality == pytest.approx(0.0)
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('hub', 'p1', 0.5, 0.8)")
```

**Verification:**
```python
assert by_id['isolated'].final_bit_width == 2
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('isolated', 'p1', 0.0, 0.0)")
```

**Verification:**
```python
assert by_id['isolated'].action == 'downgrade'
```

### Step 5: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('hub', 'p1', 32)")
```

### Step 6: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('isolated', 'p1', 32)")
```

### Step 7: Call conn.commit()

```python
conn.commit()
```

### Step 8: Assign q = ActivationGuidedQuantizer(...)

```python
q = ActivationGuidedQuantizer(test_db, sagq_config)
```

### Step 9: Assign result = q.compute_sagq_precision_batch(...)

```python
result = q.compute_sagq_precision_batch('p1', eap_mapper)
```

### Step 10: Assign by_id = value

```python
by_id = {p.fact_id: p for p in result}
```

**Verification:**
```python
assert by_id['isolated'].sagq_bit_width == 2
```


## Complete Example

```python
# Setup
# Fixtures: test_db, sagq_config

# Workflow
'Fact with no edges (pr=0, deg=0, sa=0) -> centrality=0.0 -> sagq_bw=2.'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('hub', 'p1', 0.5, 0.8)")
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('isolated', 'p1', 0.0, 0.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('hub', 'p1', 32)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('isolated', 'p1', 32)")
conn.commit()
q = ActivationGuidedQuantizer(test_db, sagq_config)

def eap_mapper(fact_id: str) -> int:
    return 2
result = q.compute_sagq_precision_batch('p1', eap_mapper)
by_id = {p.fact_id: p for p in result}
assert by_id['isolated'].sagq_bit_width == 2
assert by_id['isolated'].centrality == pytest.approx(0.0)
assert by_id['isolated'].final_bit_width == 2
assert by_id['isolated'].action == 'downgrade'
```

## Next Steps


---

*Source: test_sagq.py:375 | Complexity: Advanced | Last updated: 2026-05-05*