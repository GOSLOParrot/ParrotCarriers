# How To: Remove Preserves Non Slm Hooks

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test remove preserves non slm hooks

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sys`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.hooks`

**Setup Required:**
```python
# Fixtures: settings_path
```

## Step-by-Step Guide

### Step 1: Assign non_slm = value

```python
non_slm = {'hooks': [{'type': 'command', 'command': 'prettier --write $FILE'}]}
```

**Verification:**
```python
assert len(post) == 1
```

### Step 2: Assign slm_entry = value

```python
slm_entry = {'hooks': [{'type': 'command', 'command': 'slm hook checkpoint 2>/dev/null || true'}]}
```

**Verification:**
```python
assert 'prettier' in post[0]['hooks'][0]['command']
```

### Step 3: Call _write_settings()

```python
_write_settings(settings_path, {'hooks': {'PostToolUse': [non_slm, slm_entry]}})
```

### Step 4: Call hooks_mod.remove_hooks()

```python
hooks_mod.remove_hooks()
```

### Step 5: Assign data = _read_settings(...)

```python
data = _read_settings(settings_path)
```

### Step 6: Assign post = value

```python
post = data['hooks']['PostToolUse']
```

**Verification:**
```python
assert len(post) == 1
```


## Complete Example

```python
# Setup
# Fixtures: settings_path

# Workflow
non_slm = {'hooks': [{'type': 'command', 'command': 'prettier --write $FILE'}]}
slm_entry = {'hooks': [{'type': 'command', 'command': 'slm hook checkpoint 2>/dev/null || true'}]}
_write_settings(settings_path, {'hooks': {'PostToolUse': [non_slm, slm_entry]}})
hooks_mod.remove_hooks()
data = _read_settings(settings_path)
post = data['hooks']['PostToolUse']
assert len(post) == 1
assert 'prettier' in post[0]['hooks'][0]['command']
```

## Next Steps


---

*Source: test_claude_hooks.py:360 | Complexity: Advanced | Last updated: 2026-05-05*