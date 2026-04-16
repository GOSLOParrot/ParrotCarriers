# How To: Object Preserves All Keys

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test object preserves all keys

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
data = {f'key_{i}': f'value_{i}' for i in range(10)}
```

**Verification:**
```python
assert seen_keys == expected_keys
```

### Step 2: Assign content = json.dumps(...)

```python
content = json.dumps(data)
```

### Step 3: Assign chunks = chunk_json_content(...)

```python
chunks = chunk_json_content(content, chunk_size_tokens=50, overlap_tokens=10)
```

### Step 4: Assign seen_keys = set(...)

```python
seen_keys = set()
```

### Step 5: Assign expected_keys = value

```python
expected_keys = {f'key_{i}' for i in range(10)}
```

**Verification:**
```python
assert seen_keys == expected_keys
```

### Step 6: Assign parsed = json.loads(...)

```python
parsed = json.loads(chunk)
```

### Step 7: Call seen_keys.update()

```python
seen_keys.update(parsed.keys())
```


## Complete Example

```python
# Workflow
data = {f'key_{i}': f'value_{i}' for i in range(10)}
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=50, overlap_tokens=10)
seen_keys = set()
for chunk in chunks:
    parsed = json.loads(chunk)
    seen_keys.update(parsed.keys())
expected_keys = {f'key_{i}' for i in range(10)}
assert seen_keys == expected_keys
```

## Next Steps


---

*Source: test_content_chunking.py:125 | Complexity: Intermediate | Last updated: 2026-04-12*