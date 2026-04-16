# How To: Array Splits At Element Boundaries

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test array splits at element boundaries

## Prerequisites

**Required Modules:**
- `json`
- `graphiti_core.nodes`
- `graphiti_core.utils.content_chunking`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `graphiti_core.utils`
- `random`
- `random`
- `random`
- `random`


## Step-by-Step Guide

### Step 1: Assign data = value

```python
data = [{'id': i, 'data': 'x' * 100} for i in range(20)]
```

**Verification:**
```python
assert isinstance(parsed, list)
```

### Step 2: Assign content = json.dumps(...)

```python
content = json.dumps(data)
```

**Verification:**
```python
assert 'id' in item
```

### Step 3: Assign chunks = chunk_json_content(...)

```python
chunks = chunk_json_content(content, chunk_size_tokens=100, overlap_tokens=20)
```

**Verification:**
```python
assert 'data' in item
```

### Step 4: Assign parsed = json.loads(...)

```python
parsed = json.loads(chunk)
```

**Verification:**
```python
assert isinstance(parsed, list)
```


## Complete Example

```python
# Workflow
data = [{'id': i, 'data': 'x' * 100} for i in range(20)]
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=100, overlap_tokens=20)
for chunk in chunks:
    parsed = json.loads(chunk)
    assert isinstance(parsed, list)
    for item in parsed:
        assert 'id' in item
        assert 'data' in item
```

## Next Steps


---

*Source: test_content_chunking.py:64 | Complexity: Intermediate | Last updated: 2026-04-12*