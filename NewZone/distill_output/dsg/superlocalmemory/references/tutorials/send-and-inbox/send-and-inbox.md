# How To: Send And Inbox

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test send and inbox

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
assert send_result['ok'] is True
```

### Step 2: Assign r2 = broker.register_peer(...)

```python
r2 = broker.register_peer('s2')
```

**Verification:**
```python
assert 'id' in send_result
```

### Step 3: Assign send_result = broker.send_message(...)

```python
send_result = broker.send_message(r1['peer_id'], r2['peer_id'], 'hello')
```

**Verification:**
```python
assert len(inbox) == 1
```

### Step 4: Assign inbox = broker.get_inbox(...)

```python
inbox = broker.get_inbox(r2['peer_id'])
```

**Verification:**
```python
assert inbox[0]['content'] == 'hello'
```


## Complete Example

```python
# Setup
# Fixtures: broker

# Workflow
r1 = broker.register_peer('s1')
r2 = broker.register_peer('s2')
send_result = broker.send_message(r1['peer_id'], r2['peer_id'], 'hello')
assert send_result['ok'] is True
assert 'id' in send_result
inbox = broker.get_inbox(r2['peer_id'])
assert len(inbox) == 1
assert inbox[0]['content'] == 'hello'
```

## Next Steps


---

*Source: test_mesh.py:85 | Complexity: Intermediate | Last updated: 2026-05-05*