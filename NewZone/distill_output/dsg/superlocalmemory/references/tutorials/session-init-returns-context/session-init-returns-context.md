# How To: Session Init Returns Context

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: session_init returns success=True with a context string.

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
# Fixtures: MockAutoRecall, MockRulesEngine, _ar_create, _re_create, mock_register, mock_emit
```

## Step-by-Step Guide

### Step 1: 'session_init returns success=True with a context string.'

```python
'session_init returns success=True with a context string.'
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
assert 'context' in result
```

### Step 3: Assign auto = _make_auto_recall_mock(...)

```python
auto = _make_auto_recall_mock(context='# Relevant Memory Context')
```

### Step 4: Assign rules = _make_rules_mock(...)

```python
rules = _make_rules_mock()
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

**Verification:**
```python
assert result['success'] is True
```

### Step 9: Assign result = asyncio.run(...)

```python
result = asyncio.run(session_init())
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, _ar_create, _re_create, mock_register, mock_emit

# Workflow
'session_init returns success=True with a context string.'
engine = _make_engine_mock()
auto = _make_auto_recall_mock(context='# Relevant Memory Context')
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
with patch('superlocalmemory.hooks.auto_recall.AutoRecall', return_value=auto), patch('superlocalmemory.hooks.rules_engine.RulesEngine', return_value=rules):
    result = asyncio.run(session_init())
assert result['success'] is True
assert 'context' in result
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:95 | Complexity: Advanced | Last updated: 2026-05-05*