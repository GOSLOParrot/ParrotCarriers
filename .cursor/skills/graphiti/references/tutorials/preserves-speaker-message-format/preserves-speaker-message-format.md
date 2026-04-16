# How To: Preserves Speaker Message Format

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test preserves speaker message format

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
messages = [f'Speaker{i}: This is message number {i}.' for i in range(10)]
```

**Verification:**
```python
assert ':' in line
```

### Step 2: Assign content = unknown.join(...)

```python
content = '\n'.join(messages)
```

### Step 3: Assign chunks = chunk_message_content(...)

```python
chunks = chunk_message_content(content, chunk_size_tokens=50, overlap_tokens=10)
```

### Step 4: Assign lines = value

```python
lines = [line for line in chunk.split('\n') if line.strip()]
```

**Verification:**
```python
assert ':' in line
```


## Complete Example

```python
# Workflow
messages = [f'Speaker{i}: This is message number {i}.' for i in range(10)]
content = '\n'.join(messages)
chunks = chunk_message_content(content, chunk_size_tokens=50, overlap_tokens=10)
for chunk in chunks:
    lines = [line for line in chunk.split('\n') if line.strip()]
    for line in lines:
        assert ':' in line
```

## Next Steps


---

*Source: test_content_chunking.py:209 | Complexity: Intermediate | Last updated: 2026-04-12*