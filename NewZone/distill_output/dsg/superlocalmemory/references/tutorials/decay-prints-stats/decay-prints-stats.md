# How To: Decay Prints Stats

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: decay command prints zone distribution table.

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

### Step 1: 'decay command prints zone distribution table.'

```python
'decay command prints zone distribution table.'
```

**Verification:**
```python
assert '100' in captured.out
```

### Step 2: Assign config = _mock_config(...)

```python
config = _mock_config()
```

**Verification:**
```python
assert 'Active' in captured.out
```

### Step 3: Assign engine = _mock_engine(...)

```python
engine = _mock_engine()
```

**Verification:**
```python
assert 'Transitions' in captured.out
```

### Step 4: Assign mock_result = value

```python
mock_result = {'total': 100, 'active': 50, 'warm': 20, 'cold': 15, 'archive': 10, 'forgotten': 5, 'transitions': 8}
```

### Step 5: Assign captured = capsys.readouterr(...)

```python
captured = capsys.readouterr()
```

**Verification:**
```python
assert '100' in captured.out
```

### Step 6: Assign MockSched.return_value.run_decay_cycle.return_value = mock_result

```python
MockSched.return_value.run_decay_cycle.return_value = mock_result
```

### Step 7: Call cmd_decay()

```python
cmd_decay(Namespace(dry_run=True, profile='', json=False))
```


## Complete Example

```python
# Setup
# Fixtures: capsys

# Workflow
'decay command prints zone distribution table.'
config = _mock_config()
engine = _mock_engine()
mock_result = {'total': 100, 'active': 50, 'warm': 20, 'cold': 15, 'archive': 10, 'forgotten': 5, 'transitions': 8}
with patch('superlocalmemory.core.engine.MemoryEngine', return_value=engine), patch('superlocalmemory.core.config.SLMConfig.load', return_value=config), patch('superlocalmemory.learning.forgetting_scheduler.ForgettingScheduler') as MockSched, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'):
    MockSched.return_value.run_decay_cycle.return_value = mock_result
    from superlocalmemory.cli.commands import cmd_decay
    cmd_decay(Namespace(dry_run=True, profile='', json=False))
captured = capsys.readouterr()
assert '100' in captured.out
assert 'Active' in captured.out
assert 'Transitions' in captured.out
```

## Next Steps


---

*Source: test_cli_v33.py:148 | Complexity: Intermediate | Last updated: 2026-05-05*