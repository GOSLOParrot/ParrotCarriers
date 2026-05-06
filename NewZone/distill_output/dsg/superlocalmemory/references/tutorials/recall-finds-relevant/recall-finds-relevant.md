# How To: Recall Finds Relevant

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Recall 'What does Alice do?' returns engineer/Google/work in results.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `time`
- `pathlib`
- `typing`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.llm.backbone`
- `superlocalmemory.storage.models`
- `httpx`
- `httpx`
- `httpx`
- `warnings`

**Setup Required:**
```python
# Fixtures: loaded_engine
```

## Step-by-Step Guide

### Step 1: "Recall 'What does Alice do?' returns engineer/Google/work in results."

```python
"Recall 'What does Alice do?' returns engineer/Google/work in results."
```

**Verification:**
```python
assert isinstance(response, RecallResponse)
```

### Step 2: Assign response = loaded_engine.recall(...)

```python
response = loaded_engine.recall('What does Alice do?')
```

**Verification:**
```python
assert len(response.results) > 0, 'Recall returned zero results'
```

### Step 3: Assign all_contents = value

```python
all_contents = [r.fact.content.lower() for r in response.results]
```

**Verification:**
```python
assert found, f'Expected work-related keyword in results. Got: {all_contents}'
```

### Step 4: Assign keywords = value

```python
keywords = ['engineer', 'google', 'microsoft', 'work', 'software']
```

### Step 5: Assign found = any(...)

```python
found = any((kw in c for c in all_contents for kw in keywords))
```

**Verification:**
```python
assert found, f'Expected work-related keyword in results. Got: {all_contents}'
```


## Complete Example

```python
# Setup
# Fixtures: loaded_engine

# Workflow
"Recall 'What does Alice do?' returns engineer/Google/work in results."
response = loaded_engine.recall('What does Alice do?')
assert isinstance(response, RecallResponse)
assert len(response.results) > 0, 'Recall returned zero results'
all_contents = [r.fact.content.lower() for r in response.results]
keywords = ['engineer', 'google', 'microsoft', 'work', 'software']
found = any((kw in c for c in all_contents for kw in keywords))
assert found, f'Expected work-related keyword in results. Got: {all_contents}'
```

## Next Steps


---

*Source: test_mode_b_ollama.py:326 | Complexity: Intermediate | Last updated: 2026-05-05*