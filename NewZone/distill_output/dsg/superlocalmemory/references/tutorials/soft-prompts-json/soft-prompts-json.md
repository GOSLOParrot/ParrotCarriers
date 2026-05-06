# How To: Soft Prompts Json

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: soft-prompts --json produces valid JSON envelope.

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

### Step 1: 'soft-prompts --json produces valid JSON envelope.'

```python
'soft-prompts --json produces valid JSON envelope.'
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
assert envelope['data']['count'] == 0
```

### Step 3: Assign engine = _mock_engine(...)

```python
engine = _mock_engine()
```

### Step 4: Assign engine._db.execute.return_value = value

```python
engine._db.execute.return_value = []
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

### Step 7: Call cmd_soft_prompts()

```python
cmd_soft_prompts(Namespace(profile='', json=True))
```


## Complete Example

```python
# Setup
# Fixtures: capsys

# Workflow
'soft-prompts --json produces valid JSON envelope.'
config = _mock_config()
engine = _mock_engine()
engine._db.execute.return_value = []
with patch('superlocalmemory.core.engine.MemoryEngine', return_value=engine), patch('superlocalmemory.core.config.SLMConfig.load', return_value=config):
    from superlocalmemory.cli.commands import cmd_soft_prompts
    cmd_soft_prompts(Namespace(profile='', json=True))
captured = capsys.readouterr()
envelope = json.loads(captured.out)
assert envelope['success'] is True
assert envelope['data']['count'] == 0
```

## Next Steps


---

*Source: test_cli_v33.py:425 | Complexity: Intermediate | Last updated: 2026-05-05*