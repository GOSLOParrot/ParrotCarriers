# How To: On Consolidation Triggers Pipeline

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Calling on_consolidation_complete invokes all 4 stages
and returns status='success'.

## Prerequisites

**Required Modules:**
- `__future__`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_parameterize`
- `superlocalmemory.parameterization.pattern_extractor`
- `datetime`


## Step-by-Step Guide

### Step 1: "Calling on_consolidation_complete invokes all 4 stages\n    and returns status='success'."

```python
"Calling on_consolidation_complete invokes all 4 stages\n    and returns status='success'."
```

**Verification:**
```python
assert result['status'] == 'success'
```

### Step 2: Assign hook = _make_hook(...)

```python
hook = _make_hook()
```

**Verification:**
```python
assert result['patterns'] == 1
```

### Step 3: Assign result = hook.on_consolidation_complete(...)

```python
result = hook.on_consolidation_complete('profile_1')
```

**Verification:**
```python
assert result['prompts'] == 1
```


## Complete Example

```python
# Workflow
"Calling on_consolidation_complete invokes all 4 stages\n    and returns status='success'."
hook = _make_hook()
result = hook.on_consolidation_complete('profile_1')
assert result['status'] == 'success'
assert result['patterns'] == 1
assert result['prompts'] == 1
assert 'lifecycle' in result
```

## Next Steps


---

*Source: test_auto_parameterize.py:72 | Complexity: Beginner | Last updated: 2026-05-05*