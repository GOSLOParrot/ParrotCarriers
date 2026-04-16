# How To: Archive All Vs Normal Consolidation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test difference between archive_all and normal consolidation.

## Prerequisites

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


## Step-by-Step Guide

### Step 1: 'Test difference between archive_all and normal consolidation.'

```python
'Test difference between archive_all and normal consolidation.'
```

**Verification:**
```python
assert session1.last_consolidated == 35
```

### Step 2: Assign session1 = create_session_with_messages(...)

```python
session1 = create_session_with_messages('test:normal', 60)
```

**Verification:**
```python
assert len(session1.messages) == 60
```

### Step 3: Assign session1.last_consolidated = value

```python
session1.last_consolidated = len(session1.messages) - KEEP_COUNT
```

**Verification:**
```python
assert session2.last_consolidated == 0
```

### Step 4: Assign session2 = create_session_with_messages(...)

```python
session2 = create_session_with_messages('test:all', 60)
```

**Verification:**
```python
assert len(session2.messages) == 60
```

### Step 5: Assign session2.last_consolidated = 0

```python
session2.last_consolidated = 0
```

**Verification:**
```python
assert session1.last_consolidated == 35
```


## Complete Example

```python
# Workflow
'Test difference between archive_all and normal consolidation.'
session1 = create_session_with_messages('test:normal', 60)
session1.last_consolidated = len(session1.messages) - KEEP_COUNT
session2 = create_session_with_messages('test:all', 60)
session2.last_consolidated = 0
assert session1.last_consolidated == 35
assert len(session1.messages) == 60
assert session2.last_consolidated == 0
assert len(session2.messages) == 60
```

## Next Steps


---

*Source: test_consolidate_offset.py:305 | Complexity: Intermediate | Last updated: 2026-04-12*