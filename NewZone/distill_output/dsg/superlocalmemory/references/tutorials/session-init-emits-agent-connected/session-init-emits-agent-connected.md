# How To: Session Init Emits Agent Connected

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Event 'agent.connected' is emitted with project_path and resolved agent_id.

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

### Step 1: "Event 'agent.connected' is emitted with project_path and resolved agent_id."

```python
"Event 'agent.connected' is emitted with project_path and resolved agent_id."
```

**Verification:**
```python
assert args[0][0] == 'agent.connected'
```

### Step 2: Call monkeypatch.delenv()

```python
monkeypatch.delenv('SLM_AGENT_ID', raising=False)
```

**Verification:**
```python
assert payload['project_path'] == '/slm'
```

### Step 3: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock()
```

**Verification:**
```python
assert payload['agent_id'] == 'mcp_client'
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
asyncio.run(session_init(project_path='/slm'))
```

### Step 11: Call mock_emit.assert_called_once()

```python
mock_emit.assert_called_once()
```

### Step 12: Assign args = value

```python
args = mock_emit.call_args
```

**Verification:**
```python
assert args[0][0] == 'agent.connected'
```

### Step 13: Assign payload = value

```python
payload = args[0][1]
```

**Verification:**
```python
assert payload['project_path'] == '/slm'
```


## Complete Example

```python
# Setup
# Fixtures: MockAutoRecall, MockRulesEngine, mock_register, mock_emit, monkeypatch

# Workflow
"Event 'agent.connected' is emitted with project_path and resolved agent_id."
monkeypatch.delenv('SLM_AGENT_ID', raising=False)
engine = _make_engine_mock()
auto = _make_auto_recall_mock()
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
asyncio.run(session_init(project_path='/slm'))
mock_emit.assert_called_once()
args = mock_emit.call_args
assert args[0][0] == 'agent.connected'
payload = args[0][1]
assert payload['project_path'] == '/slm'
assert payload['agent_id'] == 'mcp_client'
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:337 | Complexity: Advanced | Last updated: 2026-05-05*