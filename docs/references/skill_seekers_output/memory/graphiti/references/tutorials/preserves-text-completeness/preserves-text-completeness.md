# How To: Preserves Text Completeness

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test preserves text completeness

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

### Step 1: Assign text = 'Alpha beta gamma delta epsilon zeta eta theta.'

```python
text = 'Alpha beta gamma delta epsilon zeta eta theta.'
```

**Verification:**
```python
assert all_words <= found_words
```

### Step 2: Assign chunks = chunk_text_content(...)

```python
chunks = chunk_text_content(text, chunk_size_tokens=10, overlap_tokens=2)
```

### Step 3: Assign all_words = set(...)

```python
all_words = set(text.replace('.', '').split())
```

### Step 4: Assign found_words = set(...)

```python
found_words = set()
```

**Verification:**
```python
assert all_words <= found_words
```

### Step 5: Call found_words.update()

```python
found_words.update(chunk.replace('.', '').split())
```


## Complete Example

```python
# Workflow
text = 'Alpha beta gamma delta epsilon zeta eta theta.'
chunks = chunk_text_content(text, chunk_size_tokens=10, overlap_tokens=2)
all_words = set(text.replace('.', '').split())
found_words = set()
for chunk in chunks:
    found_words.update(chunk.replace('.', '').split())
assert all_words <= found_words
```

## Next Steps


---

*Source: test_content_chunking.py:189 | Complexity: Intermediate | Last updated: 2026-04-12*