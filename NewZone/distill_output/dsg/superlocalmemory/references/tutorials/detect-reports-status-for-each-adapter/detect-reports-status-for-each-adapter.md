# How To: Detect Reports Status For Each Adapter

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test detect reports status for each adapter

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.hooks.ide_connector`


## Step-by-Step Guide

### Step 1: Assign a = _FakeAdapter(...)

```python
a = _FakeAdapter('a', active=True)
```

**Verification:**
```python
assert names == ['a', 'b']
```

### Step 2: Assign b = _FakeAdapter(...)

```python
b = _FakeAdapter('b', active=False)
```

**Verification:**
```python
assert statuses[0].active is True
```

### Step 3: Assign conn = CrossPlatformConnector(...)

```python
conn = CrossPlatformConnector([a, b])
```

**Verification:**
```python
assert statuses[1].active is False
```

### Step 4: Assign statuses = conn.detect(...)

```python
statuses = conn.detect()
```

### Step 5: Assign names = value

```python
names = [s.name for s in statuses]
```

**Verification:**
```python
assert names == ['a', 'b']
```


## Complete Example

```python
# Workflow
a = _FakeAdapter('a', active=True)
b = _FakeAdapter('b', active=False)
conn = CrossPlatformConnector([a, b])
statuses = conn.detect()
names = [s.name for s in statuses]
assert names == ['a', 'b']
assert statuses[0].active is True
assert statuses[1].active is False
```

## Next Steps


---

*Source: test_cross_platform_connector.py:40 | Complexity: Intermediate | Last updated: 2026-05-05*