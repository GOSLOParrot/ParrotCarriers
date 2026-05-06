# How To: Mark Read

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test mark read

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
assert inbox2[0]['read'] == 1
```

### Step 2: Assign r2 = broker.register_peer(...)

```python
r2 = broker.register_peer('s2')
```

### Step 3: Call broker.send_message()

```python
broker.send_message(r1['peer_id'], r2['peer_id'], 'hello')
```

### Step 4: Assign inbox = broker.get_inbox(...)

```python
inbox = broker.get_inbox(r2['peer_id'])
```

### Step 5: Assign msg_id = value

```python
msg_id = inbox[0]['id']
```

### Step 6: Call broker.mark_read()

```python
broker.mark_read(r2['peer_id'], [msg_id])
```

### Step 7: Assign inbox2 = broker.get_inbox(...)

```python
inbox2 = broker.get_inbox(r2['peer_id'])
```

**Verification:**
```python
assert inbox2[0]['read'] == 1
```


## Complete Example

```python
# Setup
# Fixtures: broker

# Workflow
r1 = broker.register_peer('s1')
r2 = broker.register_peer('s2')
broker.send_message(r1['peer_id'], r2['peer_id'], 'hello')
inbox = broker.get_inbox(r2['peer_id'])
msg_id = inbox[0]['id']
broker.mark_read(r2['peer_id'], [msg_id])
inbox2 = broker.get_inbox(r2['peer_id'])
assert inbox2[0]['read'] == 1
```

## Next Steps


---

*Source: test_mesh.py:101 | Complexity: Intermediate | Last updated: 2026-05-05*