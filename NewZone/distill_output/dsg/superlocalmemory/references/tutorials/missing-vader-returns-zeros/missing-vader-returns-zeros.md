# How To: Missing Vader Returns Zeros

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test missing vader returns zeros

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.encoding.emotional`
- `superlocalmemory.encoding.emotional`


## Step-by-Step Guide

### Step 1: Assign original = value

```python
original = emo_mod._vader_analyzer
```

**Verification:**
```python
assert isinstance(tag, EmotionalTag)
```

### Step 2: Assign emo_mod._vader_analyzer = None

```python
emo_mod._vader_analyzer = None
```

### Step 3: Assign emo_mod._vader_analyzer = original

```python
emo_mod._vader_analyzer = original
```

### Step 4: Assign emo_mod._vader_analyzer = None

```python
emo_mod._vader_analyzer = None
```

### Step 5: Assign tag = tag_emotion(...)

```python
tag = tag_emotion('I love this!')
```

**Verification:**
```python
assert isinstance(tag, EmotionalTag)
```


## Complete Example

```python
# Workflow
import superlocalmemory.encoding.emotional as emo_mod
original = emo_mod._vader_analyzer
emo_mod._vader_analyzer = None
try:
    with patch.dict('sys.modules', {'vaderSentiment': None, 'vaderSentiment.vaderSentiment': None}):
        emo_mod._vader_analyzer = None
        tag = tag_emotion('I love this!')
        assert isinstance(tag, EmotionalTag)
finally:
    emo_mod._vader_analyzer = original
```

## Next Steps


---

*Source: test_emotional.py:73 | Complexity: Advanced | Last updated: 2026-05-05*