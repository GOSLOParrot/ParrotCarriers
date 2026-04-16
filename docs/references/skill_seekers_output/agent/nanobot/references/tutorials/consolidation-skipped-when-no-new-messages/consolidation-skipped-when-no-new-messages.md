# How To: Consolidation Skipped When No New Messages

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test consolidation skipped when messages_to_process <= 0.

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

### Step 1: 'Test consolidation skipped when messages_to_process <= 0.'

```python
'Test consolidation skipped when messages_to_process <= 0.'
```

**Verification:**
```python
assert messages_to_process > 0
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:already_consolidated', 40)
```

**Verification:**
```python
assert len(old_messages) == 0
```

### Step 3: Assign session.last_consolidated = value

```python
session.last_consolidated = len(session.messages) - KEEP_COUNT
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
assert messages_to_process > 0
```

### Step 6: Assign session.last_consolidated = value

```python
session.last_consolidated = total_messages - KEEP_COUNT
```

### Step 7: Assign old_messages = get_old_messages(...)

```python
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
```

**Verification:**
```python
assert len(old_messages) == 0
```

### Step 8: Call session.add_message()

```python
session.add_message('user', f'msg{i}')
```


## Complete Example

```python
# Workflow
'Test consolidation skipped when messages_to_process <= 0.'
session = create_session_with_messages('test:already_consolidated', 40)
session.last_consolidated = len(session.messages) - KEEP_COUNT
for i in range(40, 42):
    session.add_message('user', f'msg{i}')
total_messages = len(session.messages)
messages_to_process = total_messages - session.last_consolidated
assert messages_to_process > 0
session.last_consolidated = total_messages - KEEP_COUNT
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
assert len(old_messages) == 0
```

## Next Steps


---

*Source: test_consolidate_offset.py:207 | Complexity: Advanced | Last updated: 2026-04-12*