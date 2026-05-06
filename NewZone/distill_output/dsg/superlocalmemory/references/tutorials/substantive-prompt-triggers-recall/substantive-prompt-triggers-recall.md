# How To: Substantive Prompt Triggers Recall

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, pytest, workflow, integration

## Overview

Workflow: Substantive prompts trigger recall and inject context.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `subprocess`
- `sys`
- `io`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.hooks.auto_recall_hook`
- `superlocalmemory.hooks.auto_recall_hook`
- `superlocalmemory.hooks.auto_recall_hook`
- `superlocalmemory.hooks.auto_recall_hook`
- `superlocalmemory.hooks.auto_recall_hook`
- `superlocalmemory.hooks.auto_recall_hook`
- `superlocalmemory.hooks.auto_recall_hook`
- `importlib`
- `sys`

**Setup Required:**
```python
# Fixtures: tmp_path, prompt
```

## Step-by-Step Guide

### Step 1: 'Substantive prompts trigger recall and inject context.'

```python
'Substantive prompts trigger recall and inject context.'
```

**Verification:**
```python
assert 'hookSpecificOutput' in result
```

### Step 2: Assign fake_results = value

```python
fake_results = [{'fact_id': 'f1', 'content': 'SLM uses WAL mode SQLite', 'score': 0.9}, {'fact_id': 'f2', 'content': 'Fencing token prevents stale writes', 'score': 0.8}, {'fact_id': 'f3', 'content': 'Queue consumer routes through pool', 'score': 0.7}]
```

**Verification:**
```python
assert output['hookEventName'] == 'UserPromptSubmit'
```

### Step 3: Assign output = value

```python
output = result['hookSpecificOutput']
```

**Verification:**
```python
assert 'SLM uses WAL mode SQLite' in ctx
```

### Step 4: Assign ctx = value

```python
ctx = output['additionalContext']
```

**Verification:**
```python
assert 'Fencing token' in ctx
```

### Step 5: Assign result = _run_hook(...)

```python
result = _run_hook(prompt, tmp_path)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, prompt

# Workflow
'Substantive prompts trigger recall and inject context.'
fake_results = [{'fact_id': 'f1', 'content': 'SLM uses WAL mode SQLite', 'score': 0.9}, {'fact_id': 'f2', 'content': 'Fencing token prevents stale writes', 'score': 0.8}, {'fact_id': 'f3', 'content': 'Queue consumer routes through pool', 'score': 0.7}]
with patch('superlocalmemory.hooks.auto_recall_hook._do_recall', return_value=fake_results):
    result = _run_hook(prompt, tmp_path)
assert 'hookSpecificOutput' in result
output = result['hookSpecificOutput']
assert output['hookEventName'] == 'UserPromptSubmit'
ctx = output['additionalContext']
assert 'SLM uses WAL mode SQLite' in ctx
assert 'Fencing token' in ctx
```

## Next Steps


---

*Source: test_auto_recall_hook.py:85 | Complexity: Intermediate | Last updated: 2026-05-05*