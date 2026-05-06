# How To: Session Init Registers Agent Default

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: _register_agent uses 'mcp_client' default when SLM_AGENT_ID is unset.

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
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit, monkeypatch
```

## Step-by-Step Guide

### Step 1: "_register_agent uses 'mcp_client' default when SLM_AGENT_ID is unset."

```python
"_register_agent uses 'mcp_client' default when SLM_AGENT_ID is unset."
```

### Step 2: Call monkeypatch.delenv()

```python
monkeypatch.delenv('SLM_AGENT_ID', raising=False)
```

### Step 3: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock(profile_id='varun')
```

### Step 4: Assign auto = _make_auto_recall_mock(...)

```python
auto = _make_auto_recall_mock()
```

### Step 5: Assign rules = _make_rules_mock(...)

```python
rules = _make_rules_mock()
```

### Step 6: Assign MockAutoRecall.return_value = auto

```python
MockAutoRecall.return_value = auto
```

### Step 7: Assign MockRulesEngine.return_value = rules

```python
MockRulesEngine.return_value = rules
```

### Step 8: Assign unknown = _get_session_init_tool(...)

```python
session_init, get_engine = _get_session_init_tool()
```

### Step 9: Assign get_engine.return_value = engine

```python
get_engine.return_value = engine
```

### Step 10: Call asyncio.run()

```python
asyncio.run(session_init())
```

### Step 11: Call mock_register.assert_called_once_with()

```python
mock_register.assert_called_once_with('mcp_client', 'varun')
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit, monkeypatch

# Workflow
"_register_agent uses 'mcp_client' default when SLM_AGENT_ID is unset."
monkeypatch.delenv('SLM_AGENT_ID', raising=False)
engine = _make_engine_mock(profile_id='varun')
auto = _make_auto_recall_mock()
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
asyncio.run(session_init())
mock_register.assert_called_once_with('mcp_client', 'varun')
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:289 | Complexity: Advanced | Last updated: 2026-05-05*