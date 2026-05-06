# How To: Session Init Disabled By Rules

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When should_recall returns False, response is empty context.

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

### Step 1: 'When should_recall returns False, response is empty context.'

```python
'When should_recall returns False, response is empty context.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock()
```

**Verification:**
```python
assert result['context'] == ''
```

### Step 3: Assign rules = _make_rules_mock(...)

```python
rules = _make_rules_mock(should_recall=False)
```

**Verification:**
```python
assert result['memories'] == []
```

### Step 4: Assign MockRulesEngine.return_value = rules

```python
MockRulesEngine.return_value = rules
```

**Verification:**
```python
assert 'disabled' in result['message'].lower()
```

### Step 5: Assign unknown = _get_session_init_tool(...)

```python
session_init, get_engine = _get_session_init_tool()
```

### Step 6: Assign get_engine.return_value = engine

```python
get_engine.return_value = engine
```

### Step 7: Assign result = asyncio.run(...)

```python
result = asyncio.run(session_init())
```

**Verification:**
```python
assert result['success'] is True
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit

# Workflow
'When should_recall returns False, response is empty context.'
engine = _make_engine_mock()
rules = _make_rules_mock(should_recall=False)
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
result = asyncio.run(session_init())
assert result['success'] is True
assert result['context'] == ''
assert result['memories'] == []
assert 'disabled' in result['message'].lower()
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:231 | Complexity: Advanced | Last updated: 2026-05-05*