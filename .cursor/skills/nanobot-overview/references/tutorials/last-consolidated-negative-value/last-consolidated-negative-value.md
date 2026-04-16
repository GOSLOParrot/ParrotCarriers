# How To: Last Consolidated Negative Value

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test behavior with negative last_consolidated (invalid state).

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

### Step 1: 'Test behavior with negative last_consolidated (invalid state).'

```python
'Test behavior with negative last_consolidated (invalid state).'
```

**Verification:**
```python
assert len(old_messages) == 2
```

### Step 2: Assign session = create_session_with_messages(...)

```python
session = create_session_with_messages('test:negative', 10)
```

**Verification:**
```python
assert old_messages[0]['content'] == 'msg5'
```

### Step 3: Assign session.last_consolidated = value

```python
session.last_consolidated = -5
```

**Verification:**
```python
assert old_messages[-1]['content'] == 'msg6'
```

### Step 4: Assign keep_count = 3

```python
keep_count = 3
```

### Step 5: Assign old_messages = get_old_messages(...)

```python
old_messages = get_old_messages(session, session.last_consolidated, keep_count)
```

**Verification:**
```python
assert len(old_messages) == 2
```


## Complete Example

```python
# Workflow
'Test behavior with negative last_consolidated (invalid state).'
session = create_session_with_messages('test:negative', 10)
session.last_consolidated = -5
keep_count = 3
old_messages = get_old_messages(session, session.last_consolidated, keep_count)
assert len(old_messages) == 2
assert old_messages[0]['content'] == 'msg5'
assert old_messages[-1]['content'] == 'msg6'
```

## Next Steps


---

*Source: test_consolidate_offset.py:241 | Complexity: Intermediate | Last updated: 2026-04-12*