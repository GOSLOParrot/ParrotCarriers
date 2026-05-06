# How To: Round1 Sufficient High Score

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test round1 sufficient high score

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.retrieval.agentic`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign results_data = _make_results(...)

```python
results_data = _make_results(10, 0.9)
```

**Verification:**
```python
assert len(results) > 0
```

### Step 2: Assign engine = _mock_engine(...)

```python
engine = _mock_engine(results_data)
```

**Verification:**
```python
assert len(retriever.rounds) == 1
```

### Step 3: Assign retriever = AgenticRetriever(...)

```python
retriever = AgenticRetriever()
```

**Verification:**
```python
assert retriever.rounds[0].is_sufficient is True
```

### Step 4: Assign results = retriever.retrieve(...)

```python
results = retriever.retrieve('query', 'default', engine, top_k=20)
```

**Verification:**
```python
assert len(results) > 0
```


## Complete Example

```python
# Workflow
results_data = _make_results(10, 0.9)
engine = _mock_engine(results_data)
retriever = AgenticRetriever()
results = retriever.retrieve('query', 'default', engine, top_k=20)
assert len(results) > 0
assert len(retriever.rounds) == 1
assert retriever.rounds[0].is_sufficient is True
```

## Next Steps


---

*Source: test_agentic.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*