# How To: No Prompts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: soft-prompts with no data prints 'No active soft prompts'.

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

### Step 1: "soft-prompts with no data prints 'No active soft prompts'."

```python
"soft-prompts with no data prints 'No active soft prompts'."
```

**Verification:**
```python
assert 'No active soft prompts' in captured.out
```

### Step 2: Assign config = _mock_config(...)

```python
config = _mock_config()
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

**Verification:**
```python
assert 'No active soft prompts' in captured.out
```

### Step 6: Call cmd_soft_prompts()

```python
cmd_soft_prompts(Namespace(profile='', json=False))
```


## Complete Example

```python
# Setup
# Fixtures: capsys

# Workflow
"soft-prompts with no data prints 'No active soft prompts'."
config = _mock_config()
engine = _mock_engine()
engine._db.execute.return_value = []
with patch('superlocalmemory.core.engine.MemoryEngine', return_value=engine), patch('superlocalmemory.core.config.SLMConfig.load', return_value=config):
    from superlocalmemory.cli.commands import cmd_soft_prompts
    cmd_soft_prompts(Namespace(profile='', json=False))
captured = capsys.readouterr()
assert 'No active soft prompts' in captured.out
```

## Next Steps


---

*Source: test_cli_v33.py:381 | Complexity: Intermediate | Last updated: 2026-05-05*