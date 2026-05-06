# How To: Brain Response Top Level Keys Are Stable

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: M-ARC-03: dashboard clients read specific top-level keys from
/api/v3/brain. A rename inside any _compute_* helper would silently
break them. Lock the key set here; any intentional addition updates
this test and gets a CHANGELOG entry.

## Prerequisites

**Required Modules:**
- `__future__`
- `ast`
- `inspect`
- `pathlib`
- `superlocalmemory.server.routes`


## Step-by-Step Guide

### Step 1: 'M-ARC-03: dashboard clients read specific top-level keys from\n    /api/v3/brain. A rename inside any _compute_* helper would silently\n    break them. Lock the key set here; any intentional addition updates\n    this test and gets a CHANGELOG entry.\n    '

```python
'M-ARC-03: dashboard clients read specific top-level keys from\n    /api/v3/brain. A rename inside any _compute_* helper would silently\n    break them. Lock the key set here; any intentional addition updates\n    this test and gets a CHANGELOG entry.\n    '
```

**Verification:**
```python
assert keys, 'failed to parse get_brain return dict'
```

### Step 2: Assign brain_py = value

```python
brain_py = Path(__file__).parent.parent.parent / 'src' / 'superlocalmemory' / 'server' / 'routes' / 'brain.py'
```

**Verification:**
```python
assert not missing, f'brain response dropped key(s): {missing}'
```

### Step 3: Assign src = brain_py.read_text(...)

```python
src = brain_py.read_text(encoding='utf-8')
```

**Verification:**
```python
assert not extra, f'brain response added unexpected key(s) {extra} — update tests/test_api/test_s9_w4_brain_contract.py + CHANGELOG'
```

### Step 4: Assign keys = _extract_return_keys(...)

```python
keys = _extract_return_keys(src)
```

**Verification:**
```python
assert keys, 'failed to parse get_brain return dict'
```

### Step 5: Assign missing = value

```python
missing = _EXPECTED_TOP_LEVEL_KEYS - keys
```

### Step 6: Assign extra = value

```python
extra = keys - _EXPECTED_TOP_LEVEL_KEYS
```

**Verification:**
```python
assert not missing, f'brain response dropped key(s): {missing}'
```


## Complete Example

```python
# Workflow
'M-ARC-03: dashboard clients read specific top-level keys from\n    /api/v3/brain. A rename inside any _compute_* helper would silently\n    break them. Lock the key set here; any intentional addition updates\n    this test and gets a CHANGELOG entry.\n    '
brain_py = Path(__file__).parent.parent.parent / 'src' / 'superlocalmemory' / 'server' / 'routes' / 'brain.py'
src = brain_py.read_text(encoding='utf-8')
keys = _extract_return_keys(src)
assert keys, 'failed to parse get_brain return dict'
missing = _EXPECTED_TOP_LEVEL_KEYS - keys
extra = keys - _EXPECTED_TOP_LEVEL_KEYS
assert not missing, f'brain response dropped key(s): {missing}'
assert not extra, f'brain response added unexpected key(s) {extra} — update tests/test_api/test_s9_w4_brain_contract.py + CHANGELOG'
```

## Next Steps


---

*Source: test_s9_w4_brain_contract.py:74 | Complexity: Advanced | Last updated: 2026-05-05*