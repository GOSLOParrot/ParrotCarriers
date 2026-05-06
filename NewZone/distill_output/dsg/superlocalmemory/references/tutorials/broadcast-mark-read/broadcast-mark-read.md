# How To: Broadcast Mark Read

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test broadcast mark read

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
assert inbox[0]['read'] == 0
```

### Step 2: Assign r2 = broker.register_peer(...)

```python
r2 = broker.register_peer('s2')
```

**Verification:**
```python
assert inbox2[0]['read'] == 1
```

### Step 3: Call broker.send_message()

```python
broker.send_message(r1['peer_id'], 'broadcast', 'read me')
```

### Step 4: Assign inbox = broker.get_inbox(...)

```python
inbox = broker.get_inbox(r2['peer_id'])
```

**Verification:**
```python
assert inbox[0]['read'] == 0
```

### Step 5: Call broker.mark_read()

```python
broker.mark_read(r2['peer_id'], [inbox[0]['id']])
```

### Step 6: Assign inbox2 = broker.get_inbox(...)

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
broker.send_message(r1['peer_id'], 'broadcast', 'read me')
inbox = broker.get_inbox(r2['peer_id'])
assert inbox[0]['read'] == 0
broker.mark_read(r2['peer_id'], [inbox[0]['id']])
inbox2 = broker.get_inbox(r2['peer_id'])
assert inbox2[0]['read'] == 1
```

## Next Steps


---

*Source: test_mesh.py:216 | Complexity: Intermediate | Last updated: 2026-05-05*