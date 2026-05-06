# How To: All Channels Contribute To Fusion

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When all 4 channels return results, fusion includes candidates from each.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'When all 4 channels return results, fusion includes candidates from each.'

```python
'When all 4 channels return results, fusion includes candidates from each.'
```

**Verification:**
```python
assert 'f_sem' in result_ids
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f_sem', 'Alice works at NovaTech as a senior architect with deep expertise'), _make_fact('f_bm25', 'Bob joined the ML team and leads the data science projects'), _make_fact('f_entity', 'Charlie mentioned the Qualixar product suite during the meeting'), _make_fact('f_temp', 'Last Tuesday the deployment pipeline was refactored completely')]
```

**Verification:**
```python
assert 'f_bm25' in result_ids
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

**Verification:**
```python
assert 'f_temp' in result_ids
```

### Step 4: Assign engine = _build_engine(...)

```python
engine = _build_engine(db=db, semantic_results=[('f_sem', 0.9)], bm25_results=[('f_bm25', 0.8)], entity_results=[('f_entity', 0.7)], temporal_results=[('f_temp', 0.6)])
```

### Step 5: Assign response = engine.recall(...)

```python
response = engine.recall('What happened?', 'default')
```

### Step 6: Assign result_ids = value

```python
result_ids = {r.fact.fact_id for r in response.results}
```

**Verification:**
```python
assert 'f_sem' in result_ids
```


## Complete Example

```python
# Workflow
'When all 4 channels return results, fusion includes candidates from each.'
facts = [_make_fact('f_sem', 'Alice works at NovaTech as a senior architect with deep expertise'), _make_fact('f_bm25', 'Bob joined the ML team and leads the data science projects'), _make_fact('f_entity', 'Charlie mentioned the Qualixar product suite during the meeting'), _make_fact('f_temp', 'Last Tuesday the deployment pipeline was refactored completely')]
db = _mock_db(facts)
engine = _build_engine(db=db, semantic_results=[('f_sem', 0.9)], bm25_results=[('f_bm25', 0.8)], entity_results=[('f_entity', 0.7)], temporal_results=[('f_temp', 0.6)])
response = engine.recall('What happened?', 'default')
result_ids = {r.fact.fact_id for r in response.results}
assert 'f_sem' in result_ids
assert 'f_bm25' in result_ids
assert 'f_temp' in result_ids
```

## Next Steps


---

*Source: test_retrieval_integration.py:116 | Complexity: Intermediate | Last updated: 2026-05-05*