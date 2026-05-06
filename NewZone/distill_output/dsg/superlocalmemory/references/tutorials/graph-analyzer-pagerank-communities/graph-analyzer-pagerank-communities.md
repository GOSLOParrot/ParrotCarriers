# How To: Graph Analyzer Pagerank Communities

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: GraphAnalyzer computes PageRank and communities.

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

### Step 1: 'GraphAnalyzer computes PageRank and communities.'

```python
'GraphAnalyzer computes PageRank and communities.'
```

**Verification:**
```python
assert isinstance(result, dict)
```

### Step 2: Assign engine = _create_v32_engine(...)

```python
engine = _create_v32_engine(tmp_path)
```

**Verification:**
```python
assert 'node_count' in result
```

### Step 3: Call engine.close()

```python
engine.close()
```

**Verification:**
```python
assert 'community_count' in result
```

### Step 4: Call engine.store()

```python
engine.store(content, session_id='s1')
```

**Verification:**
```python
assert cnt > 0, 'fact_importance table not populated'
```

### Step 5: Assign result = engine._graph_analyzer.compute_and_store(...)

```python
result = engine._graph_analyzer.compute_and_store('default')
```

**Verification:**
```python
assert isinstance(result, dict)
```

### Step 6: Assign importance = engine._db.execute(...)

```python
importance = engine._db.execute('SELECT COUNT(*) as cnt FROM fact_importance WHERE profile_id = ?', ('default',))
```

### Step 7: Assign cnt = value

```python
cnt = dict(importance[0])['cnt']
```

**Verification:**
```python
assert cnt > 0, 'fact_importance table not populated'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'GraphAnalyzer computes PageRank and communities.'
engine = _create_v32_engine(tmp_path)
for content in _SESSION_1_FACTS + _SESSION_2_FACTS:
    engine.store(content, session_id='s1')
if engine._graph_analyzer is not None:
    result = engine._graph_analyzer.compute_and_store('default')
    assert isinstance(result, dict)
    assert 'node_count' in result
    assert 'community_count' in result
    if result['node_count'] > 0:
        importance = engine._db.execute('SELECT COUNT(*) as cnt FROM fact_importance WHERE profile_id = ?', ('default',))
        cnt = dict(importance[0])['cnt']
        assert cnt > 0, 'fact_importance table not populated'
engine.close()
```

## Next Steps


---

*Source: test_e2e_v32.py:726 | Complexity: Intermediate | Last updated: 2026-05-05*