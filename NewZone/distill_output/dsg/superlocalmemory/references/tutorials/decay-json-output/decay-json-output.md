# How To: Decay Json Output

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: decay with --json produces valid JSON envelope.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `argparse`
- `dataclasses`
- `unittest.mock`
- `pytest`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`

**Setup Required:**
```python
# Fixtures: capsys
```

## Step-by-Step Guide

### Step 1: 'decay with --json produces valid JSON envelope.'

```python
'decay with --json produces valid JSON envelope.'
```

**Verification:**
```python
assert envelope['success'] is True
```

### Step 2: Assign config = _mock_config(...)

```python
config = _mock_config()
```

**Verification:**
```python
assert envelope['command'] == 'decay'
```

### Step 3: Assign engine = _mock_engine(...)

```python
engine = _mock_engine()
```

**Verification:**
```python
assert envelope['data']['total'] == 50
```

### Step 4: Assign mock_result = value

```python
mock_result = {'total': 50, 'active': 30, 'warm': 10, 'cold': 5, 'archive': 3, 'forgotten': 2, 'transitions': 4}
```

### Step 5: Assign captured = capsys.readouterr(...)

```python
captured = capsys.readouterr()
```

### Step 6: Assign envelope = json.loads(...)

```python
envelope = json.loads(captured.out)
```

**Verification:**
```python
assert envelope['success'] is True
```

### Step 7: Assign MockSched.return_value.run_decay_cycle.return_value = mock_result

```python
MockSched.return_value.run_decay_cycle.return_value = mock_result
```

### Step 8: Call cmd_decay()

```python
cmd_decay(Namespace(dry_run=True, profile='', json=True))
```


## Complete Example

```python
# Setup
# Fixtures: capsys

# Workflow
'decay with --json produces valid JSON envelope.'
config = _mock_config()
engine = _mock_engine()
mock_result = {'total': 50, 'active': 30, 'warm': 10, 'cold': 5, 'archive': 3, 'forgotten': 2, 'transitions': 4}
with patch('superlocalmemory.core.engine.MemoryEngine', return_value=engine), patch('superlocalmemory.core.config.SLMConfig.load', return_value=config), patch('superlocalmemory.learning.forgetting_scheduler.ForgettingScheduler') as MockSched, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'):
    MockSched.return_value.run_decay_cycle.return_value = mock_result
    from superlocalmemory.cli.commands import cmd_decay
    cmd_decay(Namespace(dry_run=True, profile='', json=True))
captured = capsys.readouterr()
envelope = json.loads(captured.out)
assert envelope['success'] is True
assert envelope['command'] == 'decay'
assert envelope['data']['total'] == 50
```

## Next Steps


---

*Source: test_cli_v33.py:177 | Complexity: Advanced | Last updated: 2026-05-05*