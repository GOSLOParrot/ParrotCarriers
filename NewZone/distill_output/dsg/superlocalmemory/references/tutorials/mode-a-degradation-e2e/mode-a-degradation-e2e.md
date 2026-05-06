# How To: Mode A Degradation E2E

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Verify Mode A degrades gracefully when VectorStore unavailable.

Embedding-dependent features disabled:
  - SpreadingActivation (needs vectors)
  - AutoLinker (needs cosine sim from VectorStore)

Non-embedding features work:
  - BM25 + entity_graph retrieval
  - PageRank (pure graph math)
  - Temporal validity (pure SQL)
  - Consolidation (rules-based)
  - Core Memory blocks (top-N facts)

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `dataclasses`
- `hashlib`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Verify Mode A degrades gracefully when VectorStore unavailable.\n\n        Embedding-dependent features disabled:\n          - SpreadingActivation (needs vectors)\n          - AutoLinker (needs cosine sim from VectorStore)\n\n        Non-embedding features work:\n          - BM25 + entity_graph retrieval\n          - PageRank (pure graph math)\n          - Temporal validity (pure SQL)\n          - Consolidation (rules-based)\n          - Core Memory blocks (top-N facts)\n        '

```python
'Verify Mode A degrades gracefully when VectorStore unavailable.\n\n        Embedding-dependent features disabled:\n          - SpreadingActivation (needs vectors)\n          - AutoLinker (needs cosine sim from VectorStore)\n\n        Non-embedding features work:\n          - BM25 + entity_graph retrieval\n          - PageRank (pure graph math)\n          - Temporal validity (pure SQL)\n          - Consolidation (rules-based)\n          - Core Memory blocks (top-N facts)\n        '
```

**Verification:**
```python
assert engine.fact_count >= 5
```

### Step 2: Assign config = SLMConfig.for_mode(...)

```python
config = SLMConfig.for_mode(Mode.A, base_dir=tmp_path)
```

**Verification:**
```python
assert isinstance(resp, RecallResponse)
```

### Step 3: Assign config.db_path = value

```python
config.db_path = tmp_path / 'degrade.db'
```

**Verification:**
```python
assert len(resp.results) > 0
```

### Step 4: Assign config.temporal_validator = TemporalValidatorConfig(...)

```python
config.temporal_validator = TemporalValidatorConfig(enabled=True, mode='a')
```

**Verification:**
```python
assert isinstance(is_valid, bool)
```

### Step 5: Assign config.consolidation = ConsolidationConfig(...)

```python
config.consolidation = ConsolidationConfig(enabled=True, step_count_trigger=999, promotion_min_access=0, promotion_min_trust=0.0)
```

**Verification:**
```python
assert result.get('success') is True
```

### Step 6: Assign config.retrieval = RetrievalConfig(...)

```python
config.retrieval = RetrievalConfig(use_cross_encoder=False)
```

**Verification:**
```python
assert len(blocks) >= 1
```

### Step 7: Assign engine = MemoryEngine(...)

```python
engine = MemoryEngine(config)
```

**Verification:**
```python
assert True, 'Mode A degradation completed without crashes'
```

### Step 8: Call engine.store()

```python
engine.store('DataPipe project uses Python for the backend data processing pipeline.', session_id='s1')
```

### Step 9: Call engine.store()

```python
engine.store('DataPipe connects to MongoDB for persistent storage of event streams.', session_id='s1')
```

### Step 10: Call engine.store()

```python
engine.store('Carol is the lead architect on DataPipe.', session_id='s1')
```

### Step 11: Call engine.store()

```python
engine.store('DataPipe processes 50,000 events per second.', session_id='s2')
```

### Step 12: Call engine.store()

```python
engine.store('Carol prefers event-driven architecture.', session_id='s2')
```

**Verification:**
```python
assert engine.fact_count >= 5
```

### Step 13: Assign resp = engine.recall(...)

```python
resp = engine.recall('DataPipe')
```

**Verification:**
```python
assert isinstance(resp, RecallResponse)
```

### Step 14: Call engine.close()

```python
engine.close()
```

### Step 15: Call engine.initialize()

```python
engine.initialize()
```

### Step 16: Assign engine._embedder = _DeterministicEmbedder(...)

```python
engine._embedder = _DeterministicEmbedder(768)
```

### Step 17: Assign result = engine._consolidation_engine.consolidate(...)

```python
result = engine._consolidation_engine.consolidate('default')
```

**Verification:**
```python
assert result.get('success') is True
```

### Step 18: Assign blocks = engine._db.get_core_blocks(...)

```python
blocks = engine._db.get_core_blocks('default')
```

**Verification:**
```python
assert len(blocks) >= 1
```

### Step 19: Assign is_valid = engine._temporal_validator.is_temporally_valid(...)

```python
is_valid = engine._temporal_validator.is_temporally_valid(dict(fid_row)['fact_id'], 'default')
```

**Verification:**
```python
assert isinstance(is_valid, bool)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Verify Mode A degrades gracefully when VectorStore unavailable.\n\n        Embedding-dependent features disabled:\n          - SpreadingActivation (needs vectors)\n          - AutoLinker (needs cosine sim from VectorStore)\n\n        Non-embedding features work:\n          - BM25 + entity_graph retrieval\n          - PageRank (pure graph math)\n          - Temporal validity (pure SQL)\n          - Consolidation (rules-based)\n          - Core Memory blocks (top-N facts)\n        '
config = SLMConfig.for_mode(Mode.A, base_dir=tmp_path)
config.db_path = tmp_path / 'degrade.db'
config.temporal_validator = TemporalValidatorConfig(enabled=True, mode='a')
config.consolidation = ConsolidationConfig(enabled=True, step_count_trigger=999, promotion_min_access=0, promotion_min_trust=0.0)
config.retrieval = RetrievalConfig(use_cross_encoder=False)
engine = MemoryEngine(config)
with patch('superlocalmemory.core.engine_wiring.init_embedder', return_value=_DeterministicEmbedder(768)):
    engine.initialize()
    engine._embedder = _DeterministicEmbedder(768)
engine.store('DataPipe project uses Python for the backend data processing pipeline.', session_id='s1')
engine.store('DataPipe connects to MongoDB for persistent storage of event streams.', session_id='s1')
engine.store('Carol is the lead architect on DataPipe.', session_id='s1')
engine.store('DataPipe processes 50,000 events per second.', session_id='s2')
engine.store('Carol prefers event-driven architecture.', session_id='s2')
assert engine.fact_count >= 5
resp = engine.recall('DataPipe')
assert isinstance(resp, RecallResponse)
assert len(resp.results) > 0
if engine._temporal_validator:
    for fid_row in engine._db.execute('SELECT fact_id FROM atomic_facts WHERE profile_id = ? LIMIT 3', ('default',)):
        is_valid = engine._temporal_validator.is_temporally_valid(dict(fid_row)['fact_id'], 'default')
        assert isinstance(is_valid, bool)
if engine._consolidation_engine:
    result = engine._consolidation_engine.consolidate('default')
    assert result.get('success') is True
    blocks = engine._db.get_core_blocks('default')
    assert len(blocks) >= 1
assert True, 'Mode A degradation completed without crashes'
engine.close()
```

## Next Steps


---

*Source: test_e2e_v32.py:431 | Complexity: Advanced | Last updated: 2026-05-05*