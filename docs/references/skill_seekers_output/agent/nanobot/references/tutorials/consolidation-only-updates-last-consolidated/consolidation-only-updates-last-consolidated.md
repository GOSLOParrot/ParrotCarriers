# How To: Consolidation Only Updates Last Consolidated

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that consolidation only updates last_consolidated field.

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

### Step 1: 'Test that consolidation only updates last_consolidated field.'

```python
'Test that consolidation only updates last_consolidated field.'
```

**Verification:**
```python
assert session.messages == original_messages
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:field_only', 60)
```

**Verification:**
```python
assert session.key == original_key
```

### Step 3: Assign original_messages = session.messages.copy(...)

```python
original_messages = session.messages.copy()
```

**Verification:**
```python
assert session.metadata == original_metadata
```

### Step 4: Assign original_key = value

```python
original_key = session.key
```

**Verification:**
```python
assert session.last_consolidated == 35
```

### Step 5: Assign original_metadata = session.metadata.copy(...)

```python
original_metadata = session.metadata.copy()
```

### Step 6: Assign session.last_consolidated = value

```python
session.last_consolidated = len(session.messages) - KEEP_COUNT
```

**Verification:**
```python
assert session.messages == original_messages
```


## Complete Example

```python
# Workflow
'Test that consolidation only updates last_consolidated field.'
session = create_session_with_messages('test:field_only', 60)
original_messages = session.messages.copy()
original_key = session.key
original_metadata = session.metadata.copy()
session.last_consolidated = len(session.messages) - KEEP_COUNT
assert session.messages == original_messages
assert session.key == original_key
assert session.metadata == original_metadata
assert session.last_consolidated == 35
```

## Next Steps


---

*Source: test_consolidate_offset.py:348 | Complexity: Intermediate | Last updated: 2026-04-12*