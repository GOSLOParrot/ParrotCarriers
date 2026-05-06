# How To: Recall Fn Bypasses Engine

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test recall fn bypasses engine

## Prerequisites

**Required Modules:**
- `__future__`
- `types`
- `superlocalmemory.hooks.auto_capture`
- `superlocalmemory.hooks.auto_recall`


## Step-by-Step Guide

### Step 1: Assign captured = value

```python
captured = {}
```

**Verification:**
```python
assert 'Some memory' in out
```

### Step 2: Assign auto = AutoRecall(...)

```python
auto = AutoRecall(recall_fn=fake_recall)
```

**Verification:**
```python
assert captured['query'] == 'what did we ship'
```

### Step 3: Assign out = auto.get_session_context(...)

```python
out = auto.get_session_context(query='what did we ship')
```

**Verification:**
```python
assert 'Some memory' in out
```

### Step 4: Assign unknown = query

```python
captured['query'] = query
```

### Step 5: Assign unknown = limit

```python
captured['limit'] = limit
```


## Complete Example

```python
# Workflow
captured = {}

def fake_recall(query, limit=10, **_):
    captured['query'] = query
    captured['limit'] = limit
    return _response(['f1', 'f2'], score=0.8)
auto = AutoRecall(recall_fn=fake_recall)
out = auto.get_session_context(query='what did we ship')
assert 'Some memory' in out
assert captured['query'] == 'what did we ship'
```

## Next Steps


---

*Source: test_hooks_callable_injection.py:28 | Complexity: Intermediate | Last updated: 2026-05-05*