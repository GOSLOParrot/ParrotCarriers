# How To: No Llm Returns Round1

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test no llm returns round1

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
results_data = _make_results(3, 0.1)
```

**Verification:**
```python
assert len(results) == 3
```

### Step 2: Assign engine = _mock_engine(...)

```python
engine = _mock_engine(results_data)
```

### Step 3: Assign retriever = AgenticRetriever(...)

```python
retriever = AgenticRetriever()
```

### Step 4: Assign results = retriever.retrieve(...)

```python
results = retriever.retrieve('query', 'default', engine, llm=None)
```

**Verification:**
```python
assert len(results) == 3
```


## Complete Example

```python
# Workflow
results_data = _make_results(3, 0.1)
engine = _mock_engine(results_data)
retriever = AgenticRetriever()
results = retriever.retrieve('query', 'default', engine, llm=None)
assert len(results) == 3
```

## Next Steps


---

*Source: test_agentic.py:179 | Complexity: Intermediate | Last updated: 2026-05-05*