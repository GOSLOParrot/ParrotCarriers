# How To: 5000 Facts Completes

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: 5000-fact scan completes without error. Time recorded, no strict limit.

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

### Step 1: '5000-fact scan completes without error. Time recorded, no strict limit.'

```python
'5000-fact scan completes without error. Time recorded, no strict limit.'
```

**Verification:**
```python
assert len(results) > 0, 'Expected non-empty results for 5000 facts'
```

### Step 2: Assign facts = _generate_facts(...)

```python
facts = _generate_facts(5000)
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign channel = SemanticChannel(...)

```python
channel = SemanticChannel(db)
```

### Step 5: Assign query = _make_query_embedding(...)

```python
query = _make_query_embedding()
```

### Step 6: Assign unknown = _timed_search(...)

```python
results, elapsed = _timed_search(channel, query)
```

**Verification:**
```python
assert len(results) > 0, 'Expected non-empty results for 5000 facts'
```

### Step 7: Call print()

```python
print(f'\n  [BASELINE] 5000-fact cosine scan: {elapsed:.1f}ms')
```


## Complete Example

```python
# Workflow
'5000-fact scan completes without error. Time recorded, no strict limit.'
facts = _generate_facts(5000)
db = _mock_db(facts)
channel = SemanticChannel(db)
query = _make_query_embedding()
results, elapsed = _timed_search(channel, query)
assert len(results) > 0, 'Expected non-empty results for 5000 facts'
print(f'\n  [BASELINE] 5000-fact cosine scan: {elapsed:.1f}ms')
```

## Next Steps


---

*Source: test_semantic_channel_performance.py:144 | Complexity: Intermediate | Last updated: 2026-05-05*