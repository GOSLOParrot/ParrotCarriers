# How To: Error Isolation Continues Batch

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: compress_fact failure for one fact does not block others.

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
# Fixtures: scheduler, test_db, mock_quantized_store
```

## Step-by-Step Guide

### Step 1: 'compress_fact failure for one fact does not block others.'

```python
'compress_fact failure for one fact does not block others.'
```

**Verification:**
```python
assert result.errors >= 1
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

**Verification:**
```python
assert result.downgrades >= 1
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('ref', 'p1', 1.0, 1.0)")
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('ref', 'p1', 32)")
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Assign scheduler._eap_mapper = value

```python
scheduler._eap_mapper = lambda fid: 2 if fid.startswith('err') else 32
```

### Step 7: Assign mock_quantized_store.compress_fact.side_effect = value

```python
mock_quantized_store.compress_fact.side_effect = [RuntimeError('disk full'), True, True]
```

### Step 8: Assign result = scheduler.run(...)

```python
result = scheduler.run('p1')
```

**Verification:**
```python
assert result.errors >= 1
```

### Step 9: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES (?, 'p1', 0.0, 0.0)", (f'err{i}',))
```

### Step 10: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES (?, 'p1', 32)", (f'err{i}',))
```


## Complete Example

```python
# Setup
# Fixtures: scheduler, test_db, mock_quantized_store

# Workflow
'compress_fact failure for one fact does not block others.'
conn = test_db._test_conn
for i in range(3):
    conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES (?, 'p1', 0.0, 0.0)", (f'err{i}',))
    conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES (?, 'p1', 32)", (f'err{i}',))
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('ref', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('ref', 'p1', 32)")
conn.commit()
scheduler._eap_mapper = lambda fid: 2 if fid.startswith('err') else 32
mock_quantized_store.compress_fact.side_effect = [RuntimeError('disk full'), True, True]
result = scheduler.run('p1')
assert result.errors >= 1
assert result.downgrades >= 1
```

## Next Steps


---

*Source: test_quant_scheduler.py:558 | Complexity: Advanced | Last updated: 2026-05-05*