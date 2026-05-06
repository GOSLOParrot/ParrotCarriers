# How To: Creates Start Time File

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test creates start time file

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `os`
- `sys`
- `tempfile`
- `time`
- `unittest.mock`
- `pytest`
- `superlocalmemory.hooks.hook_handlers`

**Setup Required:**
```python
# Fixtures: mock_run, mock_popen
```

## Step-by-Step Guide

### Step 1: Assign mock_run.return_value = MagicMock(...)

```python
mock_run.return_value = MagicMock(stdout='', returncode=0)
```

**Verification:**
```python
assert os.path.exists(_START_TIME)
```

### Step 2: Assign before = int(...)

```python
before = int(time.time())
```

**Verification:**
```python
assert before <= ts <= after
```

### Step 3: Call handle_hook()

```python
handle_hook('start')
```

### Step 4: Assign after = int(...)

```python
after = int(time.time())
```

**Verification:**
```python
assert os.path.exists(_START_TIME)
```

### Step 5: Assign ts = int(...)

```python
ts = int(f.read().strip())
```


## Complete Example

```python
# Setup
# Fixtures: mock_run, mock_popen

# Workflow
mock_run.return_value = MagicMock(stdout='', returncode=0)
before = int(time.time())
handle_hook('start')
after = int(time.time())
assert os.path.exists(_START_TIME)
with open(_START_TIME) as f:
    ts = int(f.read().strip())
assert before <= ts <= after
```

## Next Steps


---

*Source: test_hook_handlers.py:256 | Complexity: Intermediate | Last updated: 2026-05-05*