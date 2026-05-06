# How To: Upgrade Preserves Non Slm Hooks

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test upgrade preserves non slm hooks

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
# Fixtures: settings_path, version_file
```

## Step-by-Step Guide

### Step 1: Assign non_slm = value

```python
non_slm = {'hooks': [{'type': 'command', 'command': 'mypy --strict $FILE'}]}
```

**Verification:**
```python
assert any(('mypy' in c for c in commands))
```

### Step 2: Call hooks_mod.install_hooks()

```python
hooks_mod.install_hooks()
```

### Step 3: Assign data = _read_settings(...)

```python
data = _read_settings(settings_path)
```

### Step 4: Call unknown.insert()

```python
data['hooks']['PostToolUse'].insert(0, non_slm)
```

### Step 5: Call _write_settings()

```python
_write_settings(settings_path, data)
```

### Step 6: Call version_file.write_text()

```python
version_file.write_text('3.3.5')
```

### Step 7: Call hooks_mod.upgrade_hooks()

```python
hooks_mod.upgrade_hooks()
```

### Step 8: Assign data = _read_settings(...)

```python
data = _read_settings(settings_path)
```

### Step 9: Assign commands = value

```python
commands = [e['hooks'][0]['command'] for e in data['hooks']['PostToolUse']]
```

**Verification:**
```python
assert any(('mypy' in c for c in commands))
```


## Complete Example

```python
# Setup
# Fixtures: settings_path, version_file

# Workflow
non_slm = {'hooks': [{'type': 'command', 'command': 'mypy --strict $FILE'}]}
hooks_mod.install_hooks()
data = _read_settings(settings_path)
data['hooks']['PostToolUse'].insert(0, non_slm)
_write_settings(settings_path, data)
version_file.write_text('3.3.5')
hooks_mod.upgrade_hooks()
data = _read_settings(settings_path)
commands = [e['hooks'][0]['command'] for e in data['hooks']['PostToolUse']]
assert any(('mypy' in c for c in commands))
```

## Next Steps


---

*Source: test_claude_hooks.py:567 | Complexity: Advanced | Last updated: 2026-05-05*