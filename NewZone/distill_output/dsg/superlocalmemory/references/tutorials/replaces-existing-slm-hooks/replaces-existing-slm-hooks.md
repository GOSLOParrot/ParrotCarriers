# How To: Replaces Existing Slm Hooks

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test replaces existing slm hooks

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `sys`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.hooks`


## Step-by-Step Guide

### Step 1: Assign old_slm = value

```python
old_slm = {'hooks': [{'type': 'command', 'command': 'slm hook start 2>/dev/null || true'}]}
```

**Verification:**
```python
assert len(result['hooks']['SessionStart']) == 1
```

### Step 2: Assign settings = value

```python
settings = {'hooks': {'SessionStart': [old_slm]}}
```

### Step 3: Assign hook_defs = hooks_mod._hook_definitions(...)

```python
hook_defs = hooks_mod._hook_definitions()
```

### Step 4: Assign result = hooks_mod._merge_hooks(...)

```python
result = hooks_mod._merge_hooks(settings, hook_defs)
```

**Verification:**
```python
assert len(result['hooks']['SessionStart']) == 1
```


## Complete Example

```python
# Workflow
old_slm = {'hooks': [{'type': 'command', 'command': 'slm hook start 2>/dev/null || true'}]}
settings = {'hooks': {'SessionStart': [old_slm]}}
hook_defs = hooks_mod._hook_definitions()
result = hooks_mod._merge_hooks(settings, hook_defs)
assert len(result['hooks']['SessionStart']) == 1
```

## Next Steps


---

*Source: test_claude_hooks.py:222 | Complexity: Intermediate | Last updated: 2026-05-05*