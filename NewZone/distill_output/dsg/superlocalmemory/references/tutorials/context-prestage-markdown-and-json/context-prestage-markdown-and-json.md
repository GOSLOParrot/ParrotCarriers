# How To: Context Prestage Markdown And Json

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test context prestage markdown and json

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `argparse`
- `pathlib`
- `pytest`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.hooks.ide_connector`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.hooks.ide_connector`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.hooks`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.cli.context_commands`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch, fake_recall, capsys
```

## Step-by-Step Guide

### Step 1: Call monkeypatch.chdir()

```python
monkeypatch.chdir(tmp_path)
```

**Verification:**
```python
assert 'SLM Context' in out
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.cli.context_commands._get_recall_fn', lambda: fake_recall)
```

**Verification:**
```python
assert 'Qualixar' in out
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cp, '_now_iso', lambda: '2026-04-18T00:00:00+00:00')
```

**Verification:**
```python
assert 'topics' in data and 'entities' in data
```

### Step 4: Assign args = Namespace(...)

```python
args = Namespace(subcommand='prestage', query='what about Qualixar?', limit=5, profile_id='default', json=False, tool=False)
```

### Step 5: Call cmd_context()

```python
cmd_context(args)
```

### Step 6: Assign out = value

```python
out = capsys.readouterr().out
```

**Verification:**
```python
assert 'SLM Context' in out
```

### Step 7: Assign args2 = Namespace(...)

```python
args2 = Namespace(subcommand='prestage', query='q', limit=5, profile_id='default', json=True, tool=False)
```

### Step 8: Call cmd_context()

```python
cmd_context(args2)
```

### Step 9: Assign out2 = value

```python
out2 = capsys.readouterr().out
```

### Step 10: Assign data = json.loads(...)

```python
data = json.loads(out2)
```

**Verification:**
```python
assert 'topics' in data and 'entities' in data
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch, fake_recall, capsys

# Workflow
from superlocalmemory.cli.context_commands import cmd_context
monkeypatch.chdir(tmp_path)
monkeypatch.setattr('superlocalmemory.cli.context_commands._get_recall_fn', lambda: fake_recall)
from superlocalmemory.hooks import context_payload as cp
monkeypatch.setattr(cp, '_now_iso', lambda: '2026-04-18T00:00:00+00:00')
args = Namespace(subcommand='prestage', query='what about Qualixar?', limit=5, profile_id='default', json=False, tool=False)
cmd_context(args)
out = capsys.readouterr().out
assert 'SLM Context' in out
assert 'Qualixar' in out
args2 = Namespace(subcommand='prestage', query='q', limit=5, profile_id='default', json=True, tool=False)
cmd_context(args2)
out2 = capsys.readouterr().out
data = json.loads(out2)
assert 'topics' in data and 'entities' in data
```

## Next Steps


---

*Source: test_connect_and_prestage.py:70 | Complexity: Advanced | Last updated: 2026-05-05*