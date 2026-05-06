# How To: Connect Skips Inactive

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test connect skips inactive

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.hooks.ide_connector`


## Step-by-Step Guide

### Step 1: Assign a = _FakeAdapter(...)

```python
a = _FakeAdapter('a', active=False)
```

**Verification:**
```python
assert results['a'] == 'inactive'
```

### Step 2: Assign b = _FakeAdapter(...)

```python
b = _FakeAdapter('b', active=True, wrote=True)
```

**Verification:**
```python
assert results['b'] == 'wrote'
```

### Step 3: Assign conn = CrossPlatformConnector(...)

```python
conn = CrossPlatformConnector([a, b])
```

### Step 4: Assign results = conn.connect(...)

```python
results = conn.connect()
```

**Verification:**
```python
assert results['a'] == 'inactive'
```


## Complete Example

```python
# Workflow
a = _FakeAdapter('a', active=False)
b = _FakeAdapter('b', active=True, wrote=True)
conn = CrossPlatformConnector([a, b])
results = conn.connect()
assert results['a'] == 'inactive'
assert results['b'] == 'wrote'
```

## Next Steps


---

*Source: test_cross_platform_connector.py:58 | Complexity: Intermediate | Last updated: 2026-05-05*