# How To: Eap Upgrade To Int8 With Embedding

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Upgrade from 2-bit to int8 works when embedding is available.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.dynamics.eap_scheduler`
- `superlocalmemory.math.ebbinghaus`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.qjl`
- `superlocalmemory.storage.quantized_store`
- `json`
- `json`

**Setup Required:**
```python
# Fixtures: test_db, ebbinghaus, polar_encoder, qjl_encoder, quant_config
```

## Step-by-Step Guide

### Step 1: 'Upgrade from 2-bit to int8 works when embedding is available.'

```python
'Upgrade from 2-bit to int8 works when embedding is available.'
```

**Verification:**
```python
assert stats['upgrades'] >= 1
```

### Step 2: Call test_db._test_conn.execute()

```python
test_db._test_conn.execute('CREATE TABLE IF NOT EXISTS atomic_facts (  fact_id TEXT PRIMARY KEY,   embedding TEXT)')
```

### Step 3: Assign embedding = _random_vec.tolist(...)

```python
embedding = _random_vec(768, seed=77).tolist()
```

### Step 4: Call test_db._test_conn.execute()

```python
test_db._test_conn.execute('INSERT INTO atomic_facts (fact_id, embedding) VALUES (?, ?)', ('up-ok', json.dumps(embedding)))
```

### Step 5: Call test_db._test_conn.execute()

```python
test_db._test_conn.execute("INSERT INTO fact_retention (fact_id, profile_id, retention_score, memory_strength, access_count, lifecycle_zone) VALUES ('up-ok', 'p1', 0.6, 5.0, 3, 'warm')")
```

### Step 6: Call test_db._test_conn.execute()

```python
test_db._test_conn.execute("INSERT INTO embedding_quantization_metadata (fact_id, profile_id, quantization_level, bit_width) VALUES ('up-ok', 'p1', 'polar2', 2)")
```

### Step 7: Call test_db._test_conn.commit()

```python
test_db._test_conn.commit()
```

### Step 8: Assign qs = QuantizedEmbeddingStore(...)

```python
qs = QuantizedEmbeddingStore(test_db, polar_encoder, qjl_encoder, quant_config)
```

### Step 9: Assign scheduler = EAPScheduler(...)

```python
scheduler = EAPScheduler(test_db, ebbinghaus, qs, quant_config)
```

### Step 10: Assign stats = scheduler.run_eap_cycle(...)

```python
stats = scheduler.run_eap_cycle('p1')
```

**Verification:**
```python
assert stats['upgrades'] >= 1
```


## Complete Example

```python
# Setup
# Fixtures: test_db, ebbinghaus, polar_encoder, qjl_encoder, quant_config

# Workflow
'Upgrade from 2-bit to int8 works when embedding is available.'
import json
test_db._test_conn.execute('CREATE TABLE IF NOT EXISTS atomic_facts (  fact_id TEXT PRIMARY KEY,   embedding TEXT)')
embedding = _random_vec(768, seed=77).tolist()
test_db._test_conn.execute('INSERT INTO atomic_facts (fact_id, embedding) VALUES (?, ?)', ('up-ok', json.dumps(embedding)))
test_db._test_conn.execute("INSERT INTO fact_retention (fact_id, profile_id, retention_score, memory_strength, access_count, lifecycle_zone) VALUES ('up-ok', 'p1', 0.6, 5.0, 3, 'warm')")
test_db._test_conn.execute("INSERT INTO embedding_quantization_metadata (fact_id, profile_id, quantization_level, bit_width) VALUES ('up-ok', 'p1', 'polar2', 2)")
test_db._test_conn.commit()
qs = QuantizedEmbeddingStore(test_db, polar_encoder, qjl_encoder, quant_config)
scheduler = EAPScheduler(test_db, ebbinghaus, qs, quant_config)
stats = scheduler.run_eap_cycle('p1')
assert stats['upgrades'] >= 1
```

## Next Steps


---

*Source: test_eap_scheduler.py:447 | Complexity: Advanced | Last updated: 2026-05-05*