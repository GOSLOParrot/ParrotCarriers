# How To: Messages Added After Consolidation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test correct behavior when new messages arrive after consolidation.

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

### Step 1: 'Test correct behavior when new messages arrive after consolidation.'

```python
'Test correct behavior when new messages arrive after consolidation.'
```

**Verification:**
```python
assert len(old_messages) == expected_consolidate_count
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:new_messages', 40)
```

**Verification:**
```python
assert_messages_content(old_messages, 15, 24)
```

### Step 3: Assign session.last_consolidated = value

```python
session.last_consolidated = len(session.messages) - KEEP_COUNT
```

### Step 4: Assign total_messages = len(...)

```python
total_messages = len(session.messages)
```

### Step 5: Assign old_messages = get_old_messages(...)

```python
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
```

### Step 6: Assign expected_consolidate_count = value

```python
expected_consolidate_count = total_messages - KEEP_COUNT - session.last_consolidated
```

**Verification:**
```python
assert len(old_messages) == expected_consolidate_count
```

### Step 7: Call assert_messages_content()

```python
assert_messages_content(old_messages, 15, 24)
```

### Step 8: Call session.add_message()

```python
session.add_message('user', f'msg{i}')
```


## Complete Example

```python
# Workflow
'Test correct behavior when new messages arrive after consolidation.'
session = create_session_with_messages('test:new_messages', 40)
session.last_consolidated = len(session.messages) - KEEP_COUNT
for i in range(40, 50):
    session.add_message('user', f'msg{i}')
total_messages = len(session.messages)
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
expected_consolidate_count = total_messages - KEEP_COUNT - session.last_consolidated
assert len(old_messages) == expected_consolidate_count
assert_messages_content(old_messages, 15, 24)
```

## Next Steps


---

*Source: test_consolidate_offset.py:254 | Complexity: Advanced | Last updated: 2026-04-12*