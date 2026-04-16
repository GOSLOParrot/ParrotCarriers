# How To: Entity Rich Text Detected

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Text with many proper nouns should be detected as dense.

## Prerequisites

- [ ] Setup code must be executed first

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

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Text with many proper nouns should be detected as dense.'

```python
'Text with many proper nouns should be detected as dense.'
```

**Verification:**
```python
assert _text_likely_dense(text, tokens)
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(content_chunking, 'CHUNK_DENSITY_THRESHOLD', 0.01)
```

### Step 3: Assign text = 'Alice met Bob at Acme Corp. Then Carol and David joined them. '

```python
text = 'Alice met Bob at Acme Corp. Then Carol and David joined them. '
```

### Step 4: Assign text = value

```python
text = text * 10
```

### Step 5: Assign tokens = estimate_tokens(...)

```python
tokens = estimate_tokens(text)
```

**Verification:**
```python
assert _text_likely_dense(text, tokens)
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'Text with many proper nouns should be detected as dense.'
from graphiti_core.utils import content_chunking
monkeypatch.setattr(content_chunking, 'CHUNK_DENSITY_THRESHOLD', 0.01)
text = 'Alice met Bob at Acme Corp. Then Carol and David joined them. '
text += 'Eve from Globex introduced Frank and Grace. '
text += 'Later Henry and Iris arrived from Initech. '
text = text * 10
tokens = estimate_tokens(text)
assert _text_likely_dense(text, tokens)
```

## Next Steps


---

*Source: test_content_chunking.py:416 | Complexity: Intermediate | Last updated: 2026-04-12*