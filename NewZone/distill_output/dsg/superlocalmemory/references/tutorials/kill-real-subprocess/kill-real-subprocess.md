# How To: Kill Real Subprocess

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test kill real subprocess

## Prerequisites

**Required Modules:**
- `__future__`
- `os`
- `subprocess`
- `sys`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.platform_utils`
- `threading`
- `time`


## Step-by-Step Guide

### Step 1: Assign proc = subprocess.Popen(...)

```python
proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

**Verification:**
```python
assert is_pid_alive(pid) is True
```

### Step 2: Assign pid = value

```python
pid = proc.pid
```

**Verification:**
```python
assert result is True
```

### Step 3: Assign result = kill_process(...)

```python
result = kill_process(pid)
```

**Verification:**
```python
assert result is True
```

### Step 4: Call proc.wait()

```python
proc.wait(timeout=5)
```


## Complete Example

```python
# Workflow
proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = proc.pid
assert is_pid_alive(pid) is True
result = kill_process(pid)
assert result is True
proc.wait(timeout=5)
```

## Next Steps


---

*Source: test_platform_utils.py:107 | Complexity: Intermediate | Last updated: 2026-05-05*