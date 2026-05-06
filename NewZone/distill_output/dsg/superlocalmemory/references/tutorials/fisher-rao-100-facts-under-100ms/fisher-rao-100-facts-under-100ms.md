# How To: Fisher Rao 100 Facts Under 100Ms

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: 100-fact Fisher-Rao scan (with variance data) under 100ms.

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

### Step 1: '100-fact Fisher-Rao scan (with variance data) under 100ms.'

```python
'100-fact Fisher-Rao scan (with variance data) under 100ms.'
```

**Verification:**
```python
assert len(results) > 0
```

### Step 2: Assign facts = _generate_facts(...)

```python
facts = _generate_facts(100, with_fisher=True, mixed_access=True)
```

**Verification:**
```python
assert elapsed < 100.0, f'Fisher-Rao 100-fact scan took {elapsed:.1f}ms (budget: 100ms)'
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign channel = SemanticChannel(...)

```python
channel = SemanticChannel(db, fisher_temperature=15.0)
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
'100-fact Fisher-Rao scan (with variance data) under 100ms.'
facts = _generate_facts(100, with_fisher=True, mixed_access=True)
db = _mock_db(facts)
channel = SemanticChannel(db, fisher_temperature=15.0)
query = _make_query_embedding()
results, elapsed = _timed_search(channel, query)
assert len(results) > 0
assert elapsed < 100.0, f'Fisher-Rao 100-fact scan took {elapsed:.1f}ms (budget: 100ms)'
```

## Next Steps


---

*Source: test_semantic_channel_performance.py:165 | Complexity: Intermediate | Last updated: 2026-05-05*