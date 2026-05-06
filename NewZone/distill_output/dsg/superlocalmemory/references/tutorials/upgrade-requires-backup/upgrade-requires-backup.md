# How To: Upgrade Requires Backup

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Upgrade is skipped when no float32 backup exists (vector store returns None).

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
# Fixtures: scheduler, test_db, mock_vector_store
```

## Step-by-Step Guide

### Step 1: 'Upgrade is skipped when no float32 backup exists (vector store returns None).'

```python
'Upgrade is skipped when no float32 backup exists (vector store returns None).'
```

**Verification:**
```python
assert result.errors >= 1 or result.skipped >= 1
```

### Step 2: Assign conn = value

```python
conn = test_db._test_conn
```

### Step 3: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('no_backup', 'p1', 1.0, 1.0)")
```

### Step 4: Call conn.execute()

```python
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('no_backup', 'p1', 4)")
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Assign scheduler._eap_mapper = value

```python
scheduler._eap_mapper = lambda fid: 32
```

### Step 7: Assign mock_vector_store.get_embedding.return_value = None

```python
mock_vector_store.get_embedding.return_value = None
```

### Step 8: Assign result = scheduler.run(...)

```python
result = scheduler.run('p1')
```

**Verification:**
```python
assert result.errors >= 1 or result.skipped >= 1
```


## Complete Example

```python
# Setup
# Fixtures: scheduler, test_db, mock_vector_store

# Workflow
'Upgrade is skipped when no float32 backup exists (vector store returns None).'
conn = test_db._test_conn
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, degree_centrality) VALUES ('no_backup', 'p1', 1.0, 1.0)")
conn.execute("INSERT INTO embedding_metadata (fact_id, profile_id, bit_width) VALUES ('no_backup', 'p1', 4)")
conn.commit()
scheduler._eap_mapper = lambda fid: 32
mock_vector_store.get_embedding.return_value = None
result = scheduler.run('p1')
assert result.errors >= 1 or result.skipped >= 1
```

## Next Steps


---

*Source: test_quant_scheduler.py:270 | Complexity: Advanced | Last updated: 2026-05-05*