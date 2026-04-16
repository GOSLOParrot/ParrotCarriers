# How To: Last Consolidated Persistence

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that last_consolidated persists across save/load.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `asyncio`
- `unittest.mock`
- `pytest`
- `pathlib`
- `nanobot.session.manager`
- `nanobot.agent.loop`
- `nanobot.bus.queue`
- `nanobot.providers.base`
- `nanobot.bus.events`
- `nanobot.bus.events`
- `nanobot.bus.events`
- `nanobot.bus.events`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test that last_consolidated persists across save/load.'

```python
'Test that last_consolidated persists across save/load.'
```

**Verification:**
```python
assert session2.last_consolidated == 15
```

### Step 2: Assign manager = SessionManager(...)

```python
manager = SessionManager(Path(tmp_path))
```

**Verification:**
```python
assert len(session2.messages) == 20
```

### Step 3: Assign session1 = create_session_with_messages(...)

```python
session1 = create_session_with_messages('test:persist', 20)
```

### Step 4: Assign session1.last_consolidated = 15

```python
session1.last_consolidated = 15
```

### Step 5: Call manager.save()

```python
manager.save(session1)
```

### Step 6: Assign session2 = manager.get_or_create(...)

```python
session2 = manager.get_or_create('test:persist')
```

**Verification:**
```python
assert session2.last_consolidated == 15
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test that last_consolidated persists across save/load.'
manager = SessionManager(Path(tmp_path))
session1 = create_session_with_messages('test:persist', 20)
session1.last_consolidated = 15
manager.save(session1)
session2 = manager.get_or_create('test:persist')
assert session2.last_consolidated == 15
assert len(session2.messages) == 20
```

## Next Steps


---

*Source: test_consolidate_offset.py:67 | Complexity: Intermediate | Last updated: 2026-04-12*