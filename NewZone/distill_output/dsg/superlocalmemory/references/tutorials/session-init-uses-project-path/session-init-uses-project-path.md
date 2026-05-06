# How To: Session Init Uses Project Path

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: project_path is forwarded to AutoRecall.get_session_context().

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

### Step 1: 'project_path is forwarded to AutoRecall.get_session_context().'

```python
'project_path is forwarded to AutoRecall.get_session_context().'
```

### Step 2: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock()
```

### Step 3: Assign auto = _make_auto_recall_mock(...)

```python
auto = _make_auto_recall_mock()
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

### Step 9: Call asyncio.run()

```python
asyncio.run(session_init(project_path='/my/project'))
```

### Step 10: Call auto.get_session_context.assert_called_once_with()

```python
auto.get_session_context.assert_called_once_with(project_path='/my/project', query='')
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit

# Workflow
'project_path is forwarded to AutoRecall.get_session_context().'
engine = _make_engine_mock()
auto = _make_auto_recall_mock()
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
asyncio.run(session_init(project_path='/my/project'))
auto.get_session_context.assert_called_once_with(project_path='/my/project', query='')
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:175 | Complexity: Advanced | Last updated: 2026-05-05*