# How To: Filler Filtered

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test filler filtered

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.fact_extractor`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign ext = self._make_extractor(...)

```python
ext = self._make_extractor(min_fact_confidence=0.0)
```

**Verification:**
```python
assert not any(('hello' in c for c in contents))
```

### Step 2: Assign turns = value

```python
turns = ['Hello there!', 'Thanks for the info.', 'Alice works at Google as an engineer.']
```

### Step 3: Assign facts = ext.extract_facts(...)

```python
facts = ext.extract_facts(turns, session_id='s1')
```

### Step 4: Assign contents = value

```python
contents = [f.content.lower() for f in facts]
```

**Verification:**
```python
assert not any(('hello' in c for c in contents))
```


## Complete Example

```python
# Workflow
ext = self._make_extractor(min_fact_confidence=0.0)
turns = ['Hello there!', 'Thanks for the info.', 'Alice works at Google as an engineer.']
facts = ext.extract_facts(turns, session_id='s1')
contents = [f.content.lower() for f in facts]
assert not any(('hello' in c for c in contents))
```

## Next Steps


---

*Source: test_fact_extractor.py:215 | Complexity: Intermediate | Last updated: 2026-05-05*