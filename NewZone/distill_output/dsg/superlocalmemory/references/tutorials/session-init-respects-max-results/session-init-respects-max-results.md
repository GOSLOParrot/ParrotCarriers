# How To: Session Init Respects Max Results

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: max_results limits how many memories are returned.

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

### Step 1: 'max_results limits how many memories are returned.'

```python
'max_results limits how many memories are returned.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Assign many_memories = value

```python
many_memories = [{'fact_id': f'f-{i}', 'content': f'mem {i}', 'score': 0.9} for i in range(20)]
```

**Verification:**
```python
assert len(result['memories']) <= 3
```

### Step 3: Assign engine = _make_engine_mock(...)

```python
engine = _make_engine_mock()
```

### Step 4: Assign auto = _make_auto_recall_mock(...)

```python
auto = _make_auto_recall_mock(memories=many_memories)
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
result = asyncio.run(session_init(max_results=3))
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
'max_results limits how many memories are returned.'
many_memories = [{'fact_id': f'f-{i}', 'content': f'mem {i}', 'score': 0.9} for i in range(20)]
engine = _make_engine_mock()
auto = _make_auto_recall_mock(memories=many_memories)
rules = _make_rules_mock()
MockAutoRecall.return_value = auto
MockRulesEngine.return_value = rules
session_init, get_engine = _get_session_init_tool()
get_engine.return_value = engine
result = asyncio.run(session_init(max_results=3))
assert result['success'] is True
assert len(result['memories']) <= 3
```

## Next Steps


---

*Source: test_mcp_session_init_tool.py:253 | Complexity: Advanced | Last updated: 2026-05-05*