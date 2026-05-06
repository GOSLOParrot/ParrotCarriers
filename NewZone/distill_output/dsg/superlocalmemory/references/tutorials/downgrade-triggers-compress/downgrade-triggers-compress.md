# How To: Downgrade Triggers Compress

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Downgrade action calls quantized_store.compress_fact with correct args.

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

### Step 1: 'Downgrade action calls quantized_store.compress_fact with correct args.'

```python
'Downgrade action calls quantized_store.compress_fact with correct args.'
```

**Verification:**
```python
assert result.downgrades >= 1
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

**Verification:**
```python
assert len(low_calls) >= 1
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('low', 'p1', 0.0, 0.0)")
```

**Verification:**
```python
assert low_calls[0][0][1] == 'p1'
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('high', 'p1', 1.0, 1.0)")
```

### Step 5: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('low', 'p1', 32)")
```

### Step 6: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('high', 'p1', 32)")
```

### Step 7: Call conn.commit()

```python
conn.commit()
```

### Step 8: Assign scheduler._eap_mapper = value

```python
scheduler._eap_mapper = lambda fid: 2 if fid == 'low' else 32
```

### Step 9: Assign result = scheduler.run(...)

```python
result = scheduler.run('p1')
```

**Verification:**
```python
assert result.downgrades >= 1
```

### Step 10: Call mock_quantized_store.compress_fact.assert_called()

```python
mock_quantized_store.compress_fact.assert_called()
```

### Step 11: Assign calls = value

```python
calls = mock_quantized_store.compress_fact.call_args_list
```

### Step 12: Assign low_calls = value

```python
low_calls = [c for c in calls if c[0][0] == 'low']
```

**Verification:**
```python
assert len(low_calls) >= 1
```


## Complete Example

```python
# Setup
# Fixtures: scheduler, test_db, mock_quantized_store, mock_vector_store

# Workflow
'Downgrade action calls quantized_store.compress_fact with correct args.'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('low', 'p1', 0.0, 0.0)")
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('high', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('low', 'p1', 32)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('high', 'p1', 32)")
conn.commit()
scheduler._eap_mapper = lambda fid: 2 if fid == 'low' else 32
result = scheduler.run('p1')
assert result.downgrades >= 1
mock_quantized_store.compress_fact.assert_called()
calls = mock_quantized_store.compress_fact.call_args_list
low_calls = [c for c in calls if c[0][0] == 'low']
assert len(low_calls) >= 1
assert low_calls[0][0][1] == 'p1'
```

## Next Steps


---

*Source: test_quant_scheduler.py:218 | Complexity: Advanced | Last updated: 2026-05-05*