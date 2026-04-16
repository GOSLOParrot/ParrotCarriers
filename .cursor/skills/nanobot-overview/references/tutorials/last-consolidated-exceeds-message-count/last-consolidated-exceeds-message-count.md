# How To: Last Consolidated Exceeds Message Count

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test behavior when last_consolidated > len(messages) (data corruption).

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

### Step 1: 'Test behavior when last_consolidated > len(messages) (data corruption).'

```python
'Test behavior when last_consolidated > len(messages) (data corruption).'
```

**Verification:**
```python
assert messages_to_process <= 0
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:corruption', 10)
```

**Verification:**
```python
assert len(old_messages) == 0
```

### Step 3: Assign session.last_consolidated = 20

```python
session.last_consolidated = 20
```

### Step 4: Assign total_messages = len(...)

```python
total_messages = len(session.messages)
```

### Step 5: Assign messages_to_process = value

```python
messages_to_process = total_messages - session.last_consolidated
```

**Verification:**
```python
assert messages_to_process <= 0
```

### Step 6: Assign old_messages = get_old_messages(...)

```python
old_messages = get_old_messages(session, session.last_consolidated, 5)
```

**Verification:**
```python
assert len(old_messages) == 0
```


## Complete Example

```python
# Workflow
'Test behavior when last_consolidated > len(messages) (data corruption).'
session = create_session_with_messages('test:corruption', 10)
session.last_consolidated = 20
total_messages = len(session.messages)
messages_to_process = total_messages - session.last_consolidated
assert messages_to_process <= 0
old_messages = get_old_messages(session, session.last_consolidated, 5)
assert len(old_messages) == 0
```

## Next Steps


---

*Source: test_consolidate_offset.py:229 | Complexity: Intermediate | Last updated: 2026-04-12*