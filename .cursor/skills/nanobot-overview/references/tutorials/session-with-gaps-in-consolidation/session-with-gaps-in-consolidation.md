# How To: Session With Gaps In Consolidation

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test session with potential gaps in consolidation history.

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

### Step 1: 'Test session with potential gaps in consolidation history.'

```python
'Test session with potential gaps in consolidation history.'
```

**Verification:**
```python
assert len(old_messages) == expected_count
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:gaps', 50)
```

**Verification:**
```python
assert_messages_content(old_messages, 10, 34)
```

### Step 3: Assign session.last_consolidated = 10

```python
session.last_consolidated = 10
```

### Step 4: Assign old_messages = get_old_messages(...)

```python
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
```

### Step 5: Assign expected_count = value

```python
expected_count = 60 - KEEP_COUNT - 10
```

**Verification:**
```python
assert len(old_messages) == expected_count
```

### Step 6: Call assert_messages_content()

```python
assert_messages_content(old_messages, 10, 34)
```

### Step 7: Call session.add_message()

```python
session.add_message('user', f'msg{i}')
```


## Complete Example

```python
# Workflow
'Test session with potential gaps in consolidation history.'
session = create_session_with_messages('test:gaps', 50)
session.last_consolidated = 10
for i in range(50, 60):
    session.add_message('user', f'msg{i}')
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
expected_count = 60 - KEEP_COUNT - 10
assert len(old_messages) == expected_count
assert_messages_content(old_messages, 10, 34)
```

## Next Steps


---

*Source: test_consolidate_offset.py:467 | Complexity: Intermediate | Last updated: 2026-04-12*