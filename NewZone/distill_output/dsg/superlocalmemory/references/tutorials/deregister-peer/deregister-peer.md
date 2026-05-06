# How To: Deregister Peer

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test deregister peer

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

### Step 1: Assign r = broker.register_peer(...)

```python
r = broker.register_peer('session-1')
```

**Verification:**
```python
assert dr['ok'] is True
```

### Step 2: Assign peer_id = value

```python
peer_id = r['peer_id']
```

**Verification:**
```python
assert len(peers) == 0
```

### Step 3: Assign dr = broker.deregister_peer(...)

```python
dr = broker.deregister_peer(peer_id)
```

**Verification:**
```python
assert dr['ok'] is True
```

### Step 4: Assign peers = broker.list_peers(...)

```python
peers = broker.list_peers()
```

**Verification:**
```python
assert len(peers) == 0
```


## Complete Example

```python
# Setup
# Fixtures: broker

# Workflow
r = broker.register_peer('session-1')
peer_id = r['peer_id']
dr = broker.deregister_peer(peer_id)
assert dr['ok'] is True
peers = broker.list_peers()
assert len(peers) == 0
```

## Next Steps


---

*Source: test_mesh.py:50 | Complexity: Intermediate | Last updated: 2026-05-05*