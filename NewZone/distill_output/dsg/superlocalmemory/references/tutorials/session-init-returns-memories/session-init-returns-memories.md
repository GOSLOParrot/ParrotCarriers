# How To: Session Init Returns Memories

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: session_init returns a memories list.

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

### Step 1: 'session_init returns a memories list.'

```python
'session_init returns a memories list.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Assign memories = value

```python
memories = [{'fact_id': 'f-1', 'content': 'decision X', 'score': 0.9}, {'fact_id': 'f-2', 'content': 'bug fix Y', 'score': 0.8}]
```

**Verification:**
```python
assert result['memory_count'] == 2
```

### Step 3: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock()
```

**Verification:**
```python
assert len(result['memories']) == 2
```

### Step 4: Assign auto = _make_auto_recall_mock(...)

```python
auto = _make_auto_recall_mock(memories=memories)
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

### Step 10: Assign result = asyncio.run(...)

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
'session_init returns a memories list.'
memories = [{'fact_id': 'f-1', 'content': 'decision X', 'score': 0.9}, {'fact_id': 'f-2', 'content': 'bug fix Y', 'score': 0.8}]
engine = _make_engine_mock()
auto = _make_auto_recall_mock(memories=memories)
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
result = asyncio.run(session_init())
assert result['success'] is True
assert result['memory_count'] == 2
assert len(result['memories']) == 2
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:121 | Complexity: Advanced | Last updated: 2026-05-05*