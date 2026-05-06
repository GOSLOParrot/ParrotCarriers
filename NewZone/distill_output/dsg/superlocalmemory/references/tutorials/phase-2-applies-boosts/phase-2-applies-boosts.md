# How To: Phase 2 Applies Boosts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test phase 2 applies boosts

## Prerequisites

**Required Modules:**
- `pytest`
- `superlocalmemory.learning.ranker`


## Step-by-Step Guide

### Step 1: Assign ranker = AdaptiveRanker(...)

```python
ranker = AdaptiveRanker(signal_count=100)
```

**Verification:**
```python
assert len(reranked) == 3
```

### Step 2: Assign results = _mock_results(...)

```python
results = _mock_results()
```

**Verification:**
```python
assert fact_ids == {'f1', 'f2', 'f3'}
```

### Step 3: Assign reranked = ranker.rerank(...)

```python
reranked = ranker.rerank(results, {})
```

**Verification:**
```python
assert len(reranked) == 3
```

### Step 4: Assign fact_ids = value

```python
fact_ids = {r['fact_id'] for r in reranked}
```

**Verification:**
```python
assert fact_ids == {'f1', 'f2', 'f3'}
```


## Complete Example

```python
# Workflow
ranker = AdaptiveRanker(signal_count=100)
results = _mock_results()
reranked = ranker.rerank(results, {})
assert len(reranked) == 3
fact_ids = {r['fact_id'] for r in reranked}
assert fact_ids == {'f1', 'f2', 'f3'}
```

## Next Steps


---

*Source: test_ranker.py:44 | Complexity: Intermediate | Last updated: 2026-05-05*