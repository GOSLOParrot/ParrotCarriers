# How To: Session Init Returns Learning Status

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: session_init returns learning.phase based on feedback count.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `asyncio`
- `unittest.mock`
- `pytest`
- `superlocalmemory.mcp.tools_active`

**Setup Required:**
```python
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit
```

## Step-by-Step Guide

### Step 1: 'session_init returns learning.phase based on feedback count.'

```python
'session_init returns learning.phase based on feedback count.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock(feedback_count=75)
```

**Verification:**
```python
assert learning['feedback_signals'] == 75
```

### Step 3: Assign auto = _make_auto_recall_mock(...)

```python
auto = _make_auto_recall_mock()
```

**Verification:**
```python
assert learning['phase'] == 2
```

### Step 4: Assign rules = _make_rules_mock(...)

```python
rules = _make_rules_mock()
```

**Verification:**
```python
assert learning['status'] == 'learning'
```

### Step 5: Assign MockAutoRecall.return_value = auto

```python
MockAutoRecall.return_value = auto
```

### Step 6: Assign MockRulesEngine.return_value = rules

```python
MockRulesEngine.return_value = rules
```

### Step 7: Assign unknown = _get_session_init_tool(...)

```python
session_init, get_engine = _get_session_init_tool()
```

### Step 8: Assign get_engine.return_value = engine

```python
get_engine.return_value = engine
```

### Step 9: Assign result = asyncio.run(...)

```python
result = asyncio.run(session_init())
```

**Verification:**
```python
assert result['success'] is True
```

### Step 10: Assign learning = value

```python
learning = result['learning']
```

**Verification:**
```python
assert learning['feedback_signals'] == 75
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit

# Workflow
'session_init returns learning.phase based on feedback count.'
engine = _make_engine_mock(feedback_count=75)
auto = _make_auto_recall_mock()
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
result = asyncio.run(session_init())
assert result['success'] is True
learning = result['learning']
assert learning['feedback_signals'] == 75
assert learning['phase'] == 2
assert learning['status'] == 'learning'
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:149 | Complexity: Advanced | Last updated: 2026-05-05*