# How To: Upgrade With Backup Succeeds

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Upgrade works when float32 backup exists.

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
# Fixtures: scheduler, test_db, mock_quantized_store, mock_vector_store
```

## Step-by-Step Guide

### Step 1: 'Upgrade works when float32 backup exists.'

```python
'Upgrade works when float32 backup exists.'
```

**Verification:**
```python
assert result.upgrades >= 1
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('has_backup', 'p1', 1.0, 1.0)")
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('has_backup', 'p1', 4)")
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Assign scheduler._eap_mapper = value

```python
scheduler._eap_mapper = lambda fid: 32
```

### Step 7: Assign mock_vector_store.get_embedding.return_value = np.random.default_rng.standard_normal.astype(...)

```python
mock_vector_store.get_embedding.return_value = np.random.default_rng(42).standard_normal(768).astype(np.float32)
```

### Step 8: Assign result = scheduler.run(...)

```python
result = scheduler.run('p1')
```

**Verification:**
```python
assert result.upgrades >= 1
```


## Complete Example

```python
# Setup
# Fixtures: scheduler, test_db, mock_quantized_store, mock_vector_store

# Workflow
'Upgrade works when float32 backup exists.'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('has_backup', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('has_backup', 'p1', 4)")
conn.commit()
scheduler._eap_mapper = lambda fid: 32
mock_vector_store.get_embedding.return_value = np.random.default_rng(42).standard_normal(768).astype(np.float32)
result = scheduler.run('p1')
assert result.upgrades >= 1
```

## Next Steps


---

*Source: test_quant_scheduler.py:300 | Complexity: Advanced | Last updated: 2026-05-05*