# How To: Overlap Present

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test overlap present

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.fact_extractor`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign turns = value

```python
turns = [f'turn_{i}' for i in range(15)]
```

**Verification:**
```python
assert len(chunks) >= 2
```

### Step 2: Assign chunks = chunk_turns(...)

```python
chunks = chunk_turns(turns, chunk_size=10, overlap=2)
```

**Verification:**
```python
assert len(first_end & second_start) > 0
```

### Step 3: Assign first_end = set(...)

```python
first_end = set(chunks[0][-2:])
```

### Step 4: Assign second_start = set(...)

```python
second_start = set(chunks[1][:2])
```

**Verification:**
```python
assert len(first_end & second_start) > 0
```


## Complete Example

```python
# Workflow
turns = [f'turn_{i}' for i in range(15)]
chunks = chunk_turns(turns, chunk_size=10, overlap=2)
assert len(chunks) >= 2
first_end = set(chunks[0][-2:])
second_start = set(chunks[1][:2])
assert len(first_end & second_start) > 0
```

## Next Steps


---

*Source: test_fact_extractor.py:62 | Complexity: Intermediate | Last updated: 2026-05-05*