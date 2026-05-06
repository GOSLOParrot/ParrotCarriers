# How To: Message Size Cap

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test message size cap

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pytest`
- `pathlib`
- `superlocalmemory.storage.schema_v343`
- `superlocalmemory.mesh.broker`
- `superlocalmemory.mesh.broker`

**Setup Required:**
```python
# Fixtures: broker
```

## Step-by-Step Guide

### Step 1: Assign r1 = broker.register_peer(...)

```python
r1 = broker.register_peer('s1')
```

**Verification:**
```python
assert result['ok'] is False
```

### Step 2: Assign r2 = broker.register_peer(...)

```python
r2 = broker.register_peer('s2')
```

**Verification:**
```python
assert 'too large' in result['error']
```

### Step 3: Assign huge_msg = value

```python
huge_msg = 'x' * 5000
```

### Step 4: Assign result = broker.send_message(...)

```python
result = broker.send_message(r1['peer_id'], r2['peer_id'], huge_msg)
```

**Verification:**
```python
assert result['ok'] is False
```


## Complete Example

```python
# Setup
# Fixtures: broker

# Workflow
r1 = broker.register_peer('s1')
r2 = broker.register_peer('s2')
huge_msg = 'x' * 5000
result = broker.send_message(r1['peer_id'], r2['peer_id'], huge_msg)
assert result['ok'] is False
assert 'too large' in result['error']
```

## Next Steps


---

*Source: test_mesh.py:279 | Complexity: Intermediate | Last updated: 2026-05-05*