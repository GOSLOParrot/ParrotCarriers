# How To: 500 Facts Under 200Ms

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: 500-fact scan should complete under 200ms.

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

### Step 1: '500-fact scan should complete under 200ms.'

```python
'500-fact scan should complete under 200ms.'
```

**Verification:**
```python
assert len(results) > 0
```

### Step 2: Assign facts = _generate_facts(...)

```python
facts = _generate_facts(500)
```

**Verification:**
```python
assert elapsed < 200.0, f'500-fact scan took {elapsed:.1f}ms (budget: 200ms)'
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
'500-fact scan should complete under 200ms.'
facts = _generate_facts(500)
db = _mock_db(facts)
channel = SemanticChannel(db)
query = _make_query_embedding()
results, elapsed = _timed_search(channel, query)
assert len(results) > 0
assert elapsed < 200.0, f'500-fact scan took {elapsed:.1f}ms (budget: 200ms)'
```

## Next Steps


---

*Source: test_semantic_channel_performance.py:122 | Complexity: Intermediate | Last updated: 2026-05-05*