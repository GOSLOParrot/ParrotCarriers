# How To: Postprocess Not Called On Empty

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test postprocess not called on empty

## Prerequisites

**Required Modules:**
- `__future__`
- `io`
- `json`
- `os`
- `sys`
- `tempfile`
- `time`
- `unittest.mock`
- `pytest`
- `superlocalmemory.hooks.hook_handlers`


## Step-by-Step Guide

### Step 1: Assign called = value

```python
called = []
```

**Verification:**
```python
assert called == []
```

### Step 2: Call _run_quiet()

```python
_run_quiet(['__nonexistent__'], postprocess=lambda s: called.append(1))
```

**Verification:**
```python
assert called == []
```


## Complete Example

```python
# Workflow
called = []
_run_quiet(['__nonexistent__'], postprocess=lambda s: called.append(1))
assert called == []
```

## Next Steps


---

*Source: test_hook_handlers.py:180 | Complexity: Beginner | Last updated: 2026-05-05*