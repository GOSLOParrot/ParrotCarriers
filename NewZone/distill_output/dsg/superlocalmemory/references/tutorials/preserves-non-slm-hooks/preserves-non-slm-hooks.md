# How To: Preserves Non Slm Hooks

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test preserves non slm hooks

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

### Step 1: Assign non_slm_entry = value

```python
non_slm_entry = {'matcher': 'Write', 'hooks': [{'type': 'command', 'command': 'prettier --write $FILE'}]}
```

**Verification:**
```python
assert any(('prettier' in c for c in commands))
```

### Step 2: Assign settings = value

```python
settings = {'hooks': {'PostToolUse': [non_slm_entry]}}
```

**Verification:**
```python
assert any(('slm hook' in c for c in commands))
```

### Step 3: Assign hook_defs = hooks_mod._hook_definitions(...)

```python
hook_defs = hooks_mod._hook_definitions()
```

### Step 4: Assign result = hooks_mod._merge_hooks(...)

```python
result = hooks_mod._merge_hooks(settings, hook_defs)
```

### Step 5: Assign post_tool = value

```python
post_tool = result['hooks']['PostToolUse']
```

### Step 6: Assign commands = value

```python
commands = [e['hooks'][0]['command'] for e in post_tool]
```

**Verification:**
```python
assert any(('prettier' in c for c in commands))
```


## Complete Example

```python
# Workflow
non_slm_entry = {'matcher': 'Write', 'hooks': [{'type': 'command', 'command': 'prettier --write $FILE'}]}
settings = {'hooks': {'PostToolUse': [non_slm_entry]}}
hook_defs = hooks_mod._hook_definitions()
result = hooks_mod._merge_hooks(settings, hook_defs)
post_tool = result['hooks']['PostToolUse']
commands = [e['hooks'][0]['command'] for e in post_tool]
assert any(('prettier' in c for c in commands))
assert any(('slm hook' in c for c in commands))
```

## Next Steps


---

*Source: test_claude_hooks.py:207 | Complexity: Advanced | Last updated: 2026-05-05*