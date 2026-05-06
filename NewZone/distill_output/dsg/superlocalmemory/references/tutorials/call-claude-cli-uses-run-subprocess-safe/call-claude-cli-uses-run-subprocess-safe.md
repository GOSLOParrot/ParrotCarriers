# How To: Call Claude Cli Uses Run Subprocess Safe

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: The claude-CLI backend (if used) must go via run_subprocess_safe.

SB-4 fix — no bare subprocess.run allowed in evolution code.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.evolution`
- `superlocalmemory.evolution.llm_dispatch`
- `superlocalmemory.core`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: learning_db, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'The claude-CLI backend (if used) must go via run_subprocess_safe.\n\n    SB-4 fix — no bare subprocess.run allowed in evolution code.\n    '

```python
'The claude-CLI backend (if used) must go via run_subprocess_safe.\n\n    SB-4 fix — no bare subprocess.run allowed in evolution code.\n    '
```

**Verification:**
```python
assert out == 'safe-output'
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(secp, 'run_subprocess_safe', _fake_run_safe)
```

**Verification:**
```python
assert recorded, 'run_subprocess_safe was NOT called'
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(llm_dispatch, 'run_subprocess_safe', _fake_run_safe, raising=False)
```

**Verification:**
```python
assert recorded[0]['argv'][0] == 'claude'
```

### Step 4: Assign out = llm_dispatch._call_claude_cli_backend(...)

```python
out = llm_dispatch._call_claude_cli_backend('prompt text', model='claude-haiku-4-5', max_tokens=100)
```

**Verification:**
```python
assert isinstance(recorded[0]['env'], dict)
```

### Step 5: Call recorded.append()

```python
recorded.append({'argv': argv, 'env': env, 'timeout': timeout})
```

### Step 6: Assign self.returncode = 0

```python
self.returncode = 0
```

### Step 7: Assign self.stdout = 'safe-output'

```python
self.stdout = 'safe-output'
```

### Step 8: Assign self.stderr = ''

```python
self.stderr = ''
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, monkeypatch

# Workflow
'The claude-CLI backend (if used) must go via run_subprocess_safe.\n\n    SB-4 fix — no bare subprocess.run allowed in evolution code.\n    '
from superlocalmemory.core import security_primitives as secp
recorded: list[dict] = []

class _FakeCompleted:

    def __init__(self) -> None:
        self.returncode = 0
        self.stdout = 'safe-output'
        self.stderr = ''

def _fake_run_safe(argv, *, timeout=5.0, env=None, check=False, capture_output=True):
    recorded.append({'argv': argv, 'env': env, 'timeout': timeout})
    return _FakeCompleted()
monkeypatch.setattr(secp, 'run_subprocess_safe', _fake_run_safe)
monkeypatch.setattr(llm_dispatch, 'run_subprocess_safe', _fake_run_safe, raising=False)
out = llm_dispatch._call_claude_cli_backend('prompt text', model='claude-haiku-4-5', max_tokens=100)
assert out == 'safe-output'
assert recorded, 'run_subprocess_safe was NOT called'
assert recorded[0]['argv'][0] == 'claude'
assert isinstance(recorded[0]['env'], dict)
```

## Next Steps


---

*Source: test_llm_dispatch.py:331 | Complexity: Advanced | Last updated: 2026-05-05*