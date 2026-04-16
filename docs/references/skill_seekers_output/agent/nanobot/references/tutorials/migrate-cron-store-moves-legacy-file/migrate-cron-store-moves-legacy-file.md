# How To: Migrate Cron Store Moves Legacy File

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Legacy global jobs.json is moved into the workspace on first run.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `re`
- `pathlib`
- `unittest.mock`
- `pytest`
- `typer.testing`
- `nanobot.bus.events`
- `nanobot.cli.commands`
- `nanobot.config.schema`
- `nanobot.providers.openai_codex_provider`
- `nanobot.providers.registry`
- `shutil`
- `pytest`
- `nanobot.cli.onboard`
- `nanobot.cli.onboard`
- `nanobot.providers.openai_compat_provider`
- `nanobot.cli.commands`
- `nanobot.cli.commands`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Legacy global jobs.json is moved into the workspace on first run.'

```python
'Legacy global jobs.json is moved into the workspace on first run.'
```

**Verification:**
```python
assert workspace_cron.exists()
```

### Step 2: Assign legacy_dir = value

```python
legacy_dir = tmp_path / 'global' / 'cron'
```

**Verification:**
```python
assert workspace_cron.read_text() == '{"jobs": []}'
```

### Step 3: Call legacy_dir.mkdir()

```python
legacy_dir.mkdir(parents=True)
```

**Verification:**
```python
assert not legacy_file.exists()
```

### Step 4: Assign legacy_file = value

```python
legacy_file = legacy_dir / 'jobs.json'
```

### Step 5: Call legacy_file.write_text()

```python
legacy_file.write_text('{"jobs": []}')
```

### Step 6: Assign config = Config(...)

```python
config = Config()
```

### Step 7: Assign config.agents.defaults.workspace = str(...)

```python
config.agents.defaults.workspace = str(tmp_path / 'workspace')
```

### Step 8: Assign workspace_cron = value

```python
workspace_cron = config.workspace_path / 'cron' / 'jobs.json'
```

**Verification:**
```python
assert workspace_cron.exists()
```

### Step 9: Call _migrate_cron_store()

```python
_migrate_cron_store(config)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Legacy global jobs.json is moved into the workspace on first run.'
from nanobot.cli.commands import _migrate_cron_store
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
legacy_file = legacy_dir / 'jobs.json'
legacy_file.write_text('{"jobs": []}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'workspace')
workspace_cron = config.workspace_path / 'cron' / 'jobs.json'
with patch('nanobot.config.paths.get_cron_dir', return_value=legacy_dir):
    _migrate_cron_store(config)
assert workspace_cron.exists()
assert workspace_cron.read_text() == '{"jobs": []}'
assert not legacy_file.exists()
```

## Next Steps


---

*Source: test_commands.py:817 | Complexity: Advanced | Last updated: 2026-04-12*