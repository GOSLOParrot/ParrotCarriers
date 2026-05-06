# How To: Dispatcher Falls Back When Slm Hook Binary Disabled Set

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test dispatcher falls back when SLM HOOK BINARY DISABLED set

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `shutil`
- `stat`
- `subprocess`
- `sys`
- `textwrap`
- `pathlib`
- `pytest`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign fake_bin = value

```python
fake_bin = tmp_path / 'slm-hook'
```

**Verification:**
```python
assert 'BINARY_RAN' not in proc.stdout
```

### Step 2: Call fake_bin.write_text()

```python
fake_bin.write_text('#!/usr/bin/env bash\necho BINARY_RAN\nexit 0\n')
```

**Verification:**
```python
assert 'PYFALLBACK' in proc.stdout
```

### Step 3: Call fake_bin.chmod()

```python
fake_bin.chmod(fake_bin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
```

### Step 4: Assign unknown = _fake_python_env(...)

```python
env, _ = _fake_python_env(tmp_path)
```

### Step 5: Assign unknown = str(...)

```python
env['SLM_HOOK_BINARY'] = str(fake_bin)
```

### Step 6: Assign unknown = '1'

```python
env['SLM_HOOK_BINARY_DISABLED'] = '1'
```

### Step 7: Assign proc = _run_slm(...)

```python
proc = _run_slm(['hook', 'user_prompt_submit'], env)
```

**Verification:**
```python
assert 'BINARY_RAN' not in proc.stdout
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
fake_bin = tmp_path / 'slm-hook'
fake_bin.write_text('#!/usr/bin/env bash\necho BINARY_RAN\nexit 0\n')
fake_bin.chmod(fake_bin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
env, _ = _fake_python_env(tmp_path)
env['SLM_HOOK_BINARY'] = str(fake_bin)
env['SLM_HOOK_BINARY_DISABLED'] = '1'
proc = _run_slm(['hook', 'user_prompt_submit'], env)
assert 'BINARY_RAN' not in proc.stdout
assert 'PYFALLBACK' in proc.stdout
```

## Next Steps


---

*Source: test_dispatcher_fallback.py:82 | Complexity: Intermediate | Last updated: 2026-05-05*