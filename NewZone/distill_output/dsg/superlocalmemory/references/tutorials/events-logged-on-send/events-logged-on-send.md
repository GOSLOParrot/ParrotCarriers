# How To: Events Logged On Send

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test events logged on send

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
assert 'message_sent' in types
```

### Step 2: Assign r2 = broker.register_peer(...)

```python
r2 = broker.register_peer('s2')
```

### Step 3: Call broker.send_message()

```python
broker.send_message(r1['peer_id'], r2['peer_id'], 'hi')
```

### Step 4: Assign events = broker.get_events(...)

```python
events = broker.get_events()
```

### Step 5: Assign types = value

```python
types = [e['event_type'] for e in events]
```

**Verification:**
```python
assert 'message_sent' in types
```


## Complete Example

```python
# Setup
# Fixtures: broker

# Workflow
r1 = broker.register_peer('s1')
r2 = broker.register_peer('s2')
broker.send_message(r1['peer_id'], r2['peer_id'], 'hi')
events = broker.get_events()
types = [e['event_type'] for e in events]
assert 'message_sent' in types
```

## Next Steps


---

*Source: test_mesh.py:170 | Complexity: Intermediate | Last updated: 2026-05-05*