# How To: Json Message Array Format

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test json message array format

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

### Step 1: Assign messages = value

```python
messages = [{'role': 'user', 'content': f'Message {i}'} for i in range(10)]
```

**Verification:**
```python
assert isinstance(parsed, list)
```

### Step 2: Assign content = json.dumps(...)

```python
content = json.dumps(messages)
```

**Verification:**
```python
assert 'role' in msg
```

### Step 3: Assign chunks = chunk_message_content(...)

```python
chunks = chunk_message_content(content, chunk_size_tokens=50, overlap_tokens=10)
```

**Verification:**
```python
assert 'content' in msg
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
messages = [{'role': 'user', 'content': f'Message {i}'} for i in range(10)]
content = json.dumps(messages)
chunks = chunk_message_content(content, chunk_size_tokens=50, overlap_tokens=10)
for chunk in chunks:
    parsed = json.loads(chunk)
    assert isinstance(parsed, list)
    for msg in parsed:
        assert 'role' in msg
        assert 'content' in msg
```

## Next Steps


---

*Source: test_content_chunking.py:222 | Complexity: Intermediate | Last updated: 2026-04-12*