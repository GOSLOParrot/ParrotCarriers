# How To: Core Memory Immune To Quantization

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Fact referenced by core_memory_blocks is never downgraded (HR-01).

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

### Step 1: 'Fact referenced by core_memory_blocks is never downgraded (HR-01).'

```python
'Fact referenced by core_memory_blocks is never downgraded (HR-01).'
```

**Verification:**
```python
assert len(protected_calls) == 0
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO core_memory_blocks (block_id, profile_id, category, content, source_fact_ids) VALUES ('blk1', 'p1', 'identity', 'I am Varun', ?)", (json.dumps(['protected-fact']),))
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('protected-fact', 'p1', 0.0, 0.0)")
```

### Step 5: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('ref', 'p1', 1.0, 1.0)")
```

### Step 6: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('protected-fact', 'p1', 32)")
```

### Step 7: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('ref', 'p1', 32)")
```

### Step 8: Call conn.commit()

```python
conn.commit()
```

### Step 9: Assign scheduler._eap_mapper = value

```python
scheduler._eap_mapper = lambda fid: 2
```

### Step 10: Call mock_quantized_store.reset_mock()

```python
mock_quantized_store.reset_mock()
```

### Step 11: Assign result = scheduler.run(...)

```python
result = scheduler.run('p1')
```

### Step 12: Assign compress_calls = value

```python
compress_calls = mock_quantized_store.compress_fact.call_args_list
```

### Step 13: Assign protected_calls = value

```python
protected_calls = [c for c in compress_calls if c[0][0] == 'protected-fact']
```

**Verification:**
```python
assert len(protected_calls) == 0
```


## Complete Example

```python
# Setup
# Fixtures: scheduler, test_db, mock_quantized_store

# Workflow
'Fact referenced by core_memory_blocks is never downgraded (HR-01).'
conn = test_db._test_conn
import json
conn.execute("INSERT INTO core_memory_blocks (block_id, profile_id, category, content, source_fact_ids) VALUES ('blk1', 'p1', 'identity', 'I am Varun', ?)", (json.dumps(['protected-fact']),))
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('protected-fact', 'p1', 0.0, 0.0)")
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('ref', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('protected-fact', 'p1', 32)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('ref', 'p1', 32)")
conn.commit()
scheduler._eap_mapper = lambda fid: 2
mock_quantized_store.reset_mock()
result = scheduler.run('p1')
compress_calls = mock_quantized_store.compress_fact.call_args_list
protected_calls = [c for c in compress_calls if c[0][0] == 'protected-fact']
assert len(protected_calls) == 0
```

## Next Steps


---

*Source: test_quant_scheduler.py:424 | Complexity: Advanced | Last updated: 2026-05-05*