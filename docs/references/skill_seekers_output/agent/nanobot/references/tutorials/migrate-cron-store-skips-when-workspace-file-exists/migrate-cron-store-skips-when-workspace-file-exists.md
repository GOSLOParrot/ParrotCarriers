# How To: Migrate Cron Store Skips When Workspace File Exists

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Migration does not overwrite an existing workspace cron store.

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

### Step 1: 'Migration does not overwrite an existing workspace cron store.'

```python
'Migration does not overwrite an existing workspace cron store.'
```

**Verification:**
```python
assert workspace_cron.read_text() == '{"new": true}'
```

### Step 2: Assign legacy_dir = value

```python
legacy_dir = tmp_path / 'global' / 'cron'
```

### Step 3: Call legacy_dir.mkdir()

```python
legacy_dir.mkdir(parents=True)
```

### Step 4: Call unknown.write_text()

```python
(legacy_dir / 'jobs.json').write_text('{"old": true}')
```

### Step 5: Assign config = Config(...)

```python
config = Config()
```

### Step 6: Assign config.agents.defaults.workspace = str(...)

```python
config.agents.defaults.workspace = str(tmp_path / 'workspace')
```

### Step 7: Assign workspace_cron = value

```python
workspace_cron = config.workspace_path / 'cron' / 'jobs.json'
```

### Step 8: Call workspace_cron.parent.mkdir()

```python
workspace_cron.parent.mkdir(parents=True)
```

### Step 9: Call workspace_cron.write_text()

```python
workspace_cron.write_text('{"new": true}')
```

**Verification:**
```python
assert workspace_cron.read_text() == '{"new": true}'
```

### Step 10: Call _migrate_cron_store()

```python
_migrate_cron_store(config)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Migration does not overwrite an existing workspace cron store.'
from nanobot.cli.commands import _migrate_cron_store
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
(legacy_dir / 'jobs.json').write_text('{"old": true}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'workspace')
workspace_cron = config.workspace_path / 'cron' / 'jobs.json'
workspace_cron.parent.mkdir(parents=True)
workspace_cron.write_text('{"new": true}')
with patch('nanobot.config.paths.get_cron_dir', return_value=legacy_dir):
    _migrate_cron_store(config)
assert workspace_cron.read_text() == '{"new": true}'
```

## Next Steps


---

*Source: test_commands.py:838 | Complexity: Advanced | Last updated: 2026-04-12*