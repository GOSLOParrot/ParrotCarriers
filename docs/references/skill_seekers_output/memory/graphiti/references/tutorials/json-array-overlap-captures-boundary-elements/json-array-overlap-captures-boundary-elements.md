# How To: Json Array Overlap Captures Boundary Elements

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test json array overlap captures boundary elements

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
data = [{'id': i, 'name': f'Entity {i}'} for i in range(10)]
```

### Step 2: Assign content = json.dumps(...)

```python
content = json.dumps(data)
```

### Step 3: Assign chunks = chunk_json_content(...)

```python
chunks = chunk_json_content(content, chunk_size_tokens=80, overlap_tokens=30)
```

### Step 4: Assign current = json.loads(...)

```python
current = json.loads(chunks[i])
```

### Step 5: Assign next_chunk = json.loads(...)

```python
next_chunk = json.loads(chunks[i + 1])
```

### Step 6: Assign current_ids = value

```python
current_ids = {item['id'] for item in current}
```

### Step 7: Assign next_ids = value

```python
next_ids = {item['id'] for item in next_chunk}
```

### Step 8: Assign _ = value

```python
_ = current_ids & next_ids
```


## Complete Example

```python
# Workflow
data = [{'id': i, 'name': f'Entity {i}'} for i in range(10)]
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=80, overlap_tokens=30)
if len(chunks) > 1:
    for i in range(len(chunks) - 1):
        current = json.loads(chunks[i])
        next_chunk = json.loads(chunks[i + 1])
        current_ids = {item['id'] for item in current}
        next_ids = {item['id'] for item in next_chunk}
        _ = current_ids & next_ids
```

## Next Steps


---

*Source: test_content_chunking.py:238 | Complexity: Advanced | Last updated: 2026-04-12*