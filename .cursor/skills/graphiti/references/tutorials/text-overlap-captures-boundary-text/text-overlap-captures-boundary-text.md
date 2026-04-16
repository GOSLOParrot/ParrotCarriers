# How To: Text Overlap Captures Boundary Text

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test text overlap captures boundary text

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

### Step 1: Assign paragraphs = value

```python
paragraphs = [f'Paragraph {i} with some content here.' for i in range(10)]
```

**Verification:**
```python
assert len(overlap) > 0
```

### Step 2: Assign text = unknown.join(...)

```python
text = '\n\n'.join(paragraphs)
```

### Step 3: Assign chunks = chunk_text_content(...)

```python
chunks = chunk_text_content(text, chunk_size_tokens=50, overlap_tokens=20)
```

### Step 4: Assign current_words = set(...)

```python
current_words = set(chunks[i].split())
```

### Step 5: Assign next_words = set(...)

```python
next_words = set(chunks[i + 1].split())
```

### Step 6: Assign overlap = value

```python
overlap = current_words & next_words
```

**Verification:**
```python
assert len(overlap) > 0
```


## Complete Example

```python
# Workflow
paragraphs = [f'Paragraph {i} with some content here.' for i in range(10)]
text = '\n\n'.join(paragraphs)
chunks = chunk_text_content(text, chunk_size_tokens=50, overlap_tokens=20)
if len(chunks) > 1:
    for i in range(len(chunks) - 1):
        current_words = set(chunks[i].split())
        next_words = set(chunks[i + 1].split())
        overlap = current_words & next_words
        assert len(overlap) > 0
```

## Next Steps


---

*Source: test_content_chunking.py:260 | Complexity: Intermediate | Last updated: 2026-04-12*