# How To: Cosine Vs Fisher Ratio

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Fisher-Rao should be less than 3x slower than pure cosine for 100 facts.

## Prerequisites

**Required Modules:**
- `__future__`
- `time`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.semantic_channel`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Fisher-Rao should be less than 3x slower than pure cosine for 100 facts.'

```python
'Fisher-Rao should be less than 3x slower than pure cosine for 100 facts.'
```

**Verification:**
```python
assert ratio < 5.0, f'Fisher-Rao is {ratio:.1f}x slower than cosine (cosine={cosine_ms:.1f}ms, fisher={fisher_ms:.1f}ms)'
```

### Step 2: Assign n = 100

```python
n = 100
```

### Step 3: Assign cosine_facts = _generate_facts(...)

```python
cosine_facts = _generate_facts(n, with_fisher=False)
```

### Step 4: Assign fisher_facts = _generate_facts(...)

```python
fisher_facts = _generate_facts(n, with_fisher=True, mixed_access=True)
```

### Step 5: Assign query = _make_query_embedding(...)

```python
query = _make_query_embedding()
```

### Step 6: Assign db_cos = _mock_db(...)

```python
db_cos = _mock_db(cosine_facts)
```

### Step 7: Assign ch_cos = SemanticChannel(...)

```python
ch_cos = SemanticChannel(db_cos)
```

### Step 8: Assign unknown = _timed_search(...)

```python
_, cosine_ms = _timed_search(ch_cos, query)
```

### Step 9: Assign db_fr = _mock_db(...)

```python
db_fr = _mock_db(fisher_facts)
```

### Step 10: Assign ch_fr = SemanticChannel(...)

```python
ch_fr = SemanticChannel(db_fr, fisher_temperature=15.0)
```

### Step 11: Assign unknown = _timed_search(...)

```python
_, fisher_ms = _timed_search(ch_fr, query)
```

### Step 12: Assign ratio = value

```python
ratio = fisher_ms / cosine_ms
```

**Verification:**
```python
assert ratio < 5.0, f'Fisher-Rao is {ratio:.1f}x slower than cosine (cosine={cosine_ms:.1f}ms, fisher={fisher_ms:.1f}ms)'
```

### Step 13: Call pytest.skip()

```python
pytest.skip('Cosine scan too fast to measure ratio reliably')
```


## Complete Example

```python
# Workflow
'Fisher-Rao should be less than 3x slower than pure cosine for 100 facts.'
n = 100
cosine_facts = _generate_facts(n, with_fisher=False)
fisher_facts = _generate_facts(n, with_fisher=True, mixed_access=True)
query = _make_query_embedding()
db_cos = _mock_db(cosine_facts)
ch_cos = SemanticChannel(db_cos)
_, cosine_ms = _timed_search(ch_cos, query)
db_fr = _mock_db(fisher_facts)
ch_fr = SemanticChannel(db_fr, fisher_temperature=15.0)
_, fisher_ms = _timed_search(ch_fr, query)
if cosine_ms < 0.01:
    pytest.skip('Cosine scan too fast to measure ratio reliably')
ratio = fisher_ms / cosine_ms
assert ratio < 5.0, f'Fisher-Rao is {ratio:.1f}x slower than cosine (cosine={cosine_ms:.1f}ms, fisher={fisher_ms:.1f}ms)'
```

## Next Steps


---

*Source: test_semantic_channel_performance.py:176 | Complexity: Advanced | Last updated: 2026-05-05*