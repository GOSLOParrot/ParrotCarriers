# How To: Array Preserves All Elements

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test array preserves all elements

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
data = [{'id': i} for i in range(10)]
```

**Verification:**
```python
assert seen_ids == set(range(10))
```

### Step 2: Assign content = json.dumps(...)

```python
content = json.dumps(data)
```

### Step 3: Assign chunks = chunk_json_content(...)

```python
chunks = chunk_json_content(content, chunk_size_tokens=50, overlap_tokens=10)
```

### Step 4: Assign seen_ids = set(...)

```python
seen_ids = set()
```

**Verification:**
```python
assert seen_ids == set(range(10))
```

### Step 5: Assign parsed = json.loads(...)

```python
parsed = json.loads(chunk)
```

### Step 6: Call seen_ids.add()

```python
seen_ids.add(item['id'])
```


## Complete Example

```python
# Workflow
data = [{'id': i} for i in range(10)]
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=50, overlap_tokens=10)
seen_ids = set()
for chunk in chunks:
    parsed = json.loads(chunk)
    for item in parsed:
        seen_ids.add(item['id'])
assert seen_ids == set(range(10))
```

## Next Steps


---

*Source: test_content_chunking.py:81 | Complexity: Intermediate | Last updated: 2026-04-12*