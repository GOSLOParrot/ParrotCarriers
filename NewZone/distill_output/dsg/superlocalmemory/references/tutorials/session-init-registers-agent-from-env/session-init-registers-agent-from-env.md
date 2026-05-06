# How To: Session Init Registers Agent From Env

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: v3.4.39: SLM_AGENT_ID env overrides default for proper Avenger attribution.

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

### Step 1: 'v3.4.39: SLM_AGENT_ID env overrides default for proper Avenger attribution.'

```python
'v3.4.39: SLM_AGENT_ID env overrides default for proper Avenger attribution.'
```

### Step 2: Call monkeypatch.setenv()

```python
monkeypatch.setenv('SLM_AGENT_ID', 'codex')
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
mock_register.assert_called_once_with('codex', 'varun')
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit, monkeypatch

# Workflow
'v3.4.39: SLM_AGENT_ID env overrides default for proper Avenger attribution.'
monkeypatch.setenv('SLM_AGENT_ID', 'codex')
engine = _make_engine_mock(profile_id='varun')
auto = _make_auto_recall_mock()
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
asyncio.run(session_init())
mock_register.assert_called_once_with('codex', 'varun')
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:313 | Complexity: Advanced | Last updated: 2026-05-05*