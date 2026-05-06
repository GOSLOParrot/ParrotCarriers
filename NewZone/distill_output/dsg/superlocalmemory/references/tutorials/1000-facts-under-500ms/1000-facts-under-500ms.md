# How To: 1000 Facts Under 500Ms

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: 1000-fact scan should complete under 500ms.

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

### Step 1: '1000-fact scan should complete under 500ms.'

```python
'1000-fact scan should complete under 500ms.'
```

**Verification:**
```python
assert len(results) > 0
```

### Step 2: Assign facts = _generate_facts(...)

```python
facts = _generate_facts(1000)
```

**Verification:**
```python
assert elapsed < 500.0, f'1000-fact scan took {elapsed:.1f}ms (budget: 500ms)'
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
assert len(results) > 0
```


## Complete Example

```python
# Workflow
'1000-fact scan should complete under 500ms.'
facts = _generate_facts(1000)
db = _mock_db(facts)
channel = SemanticChannel(db)
query = _make_query_embedding()
results, elapsed = _timed_search(channel, query)
assert len(results) > 0
assert elapsed < 500.0, f'1000-fact scan took {elapsed:.1f}ms (budget: 500ms)'
```

## Next Steps


---

*Source: test_semantic_channel_performance.py:133 | Complexity: Intermediate | Last updated: 2026-05-05*