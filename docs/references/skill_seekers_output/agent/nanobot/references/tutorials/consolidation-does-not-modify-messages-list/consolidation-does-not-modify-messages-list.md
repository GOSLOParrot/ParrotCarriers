# How To: Consolidation Does Not Modify Messages List

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that consolidation leaves messages list unchanged.

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

### Step 1: 'Test that consolidation leaves messages list unchanged.'

```python
'Test that consolidation leaves messages list unchanged.'
```

**Verification:**
```python
assert len(session.messages) == original_len
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:immutable', 50)
```

**Verification:**
```python
assert session.messages == original_messages
```

### Step 3: Assign original_messages = session.messages.copy(...)

```python
original_messages = session.messages.copy()
```

### Step 4: Assign original_len = len(...)

```python
original_len = len(session.messages)
```

### Step 5: Assign session.last_consolidated = value

```python
session.last_consolidated = original_len - KEEP_COUNT
```

**Verification:**
```python
assert len(session.messages) == original_len
```


## Complete Example

```python
# Workflow
'Test that consolidation leaves messages list unchanged.'
session = create_session_with_messages('test:immutable', 50)
original_messages = session.messages.copy()
original_len = len(session.messages)
session.last_consolidated = original_len - KEEP_COUNT
assert len(session.messages) == original_len
assert session.messages == original_messages
```

## Next Steps


---

*Source: test_consolidate_offset.py:324 | Complexity: Intermediate | Last updated: 2026-04-12*