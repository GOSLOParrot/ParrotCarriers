# How To: Deduplication

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test deduplication

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
assert len(normalized) == len(set(normalized))
```

### Step 2: Assign turns = value

```python
turns = ['Alice Smith works at Google.', 'Alice Smith works at Google.']
```

### Step 3: Assign facts = ext.extract_facts(...)

```python
facts = ext.extract_facts(turns, session_id='s1')
```

### Step 4: Assign contents = value

```python
contents = [f.content for f in facts]
```

### Step 5: Assign normalized = value

```python
normalized = [c.lower().strip() for c in contents]
```

**Verification:**
```python
assert len(normalized) == len(set(normalized))
```


## Complete Example

```python
# Workflow
ext = self._make_extractor(min_fact_confidence=0.0)
turns = ['Alice Smith works at Google.', 'Alice Smith works at Google.']
facts = ext.extract_facts(turns, session_id='s1')
contents = [f.content for f in facts]
normalized = [c.lower().strip() for c in contents]
assert len(normalized) == len(set(normalized))
```

## Next Steps


---

*Source: test_fact_extractor.py:223 | Complexity: Intermediate | Last updated: 2026-05-05*