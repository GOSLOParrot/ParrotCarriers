# How To: Onboard Refresh Backfills Missing Channel Fields

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test onboard refresh backfills missing channel fields

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `nanobot.config.loader`
- `typer.testing`
- `nanobot.cli.commands`
- `types`
- `typer.testing`
- `nanobot.cli.commands`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert result.exit_code == 0
```

### Step 2: Assign workspace = value

```python
workspace = tmp_path / 'workspace'
```

**Verification:**
```python
assert saved['channels']['qq']['msgFormat'] == 'plain'
```

### Step 3: Call config_path.write_text()

```python
config_path.write_text(json.dumps({'channels': {'qq': {'enabled': False, 'appId': '', 'secret': '', 'allowFrom': []}}}), encoding='utf-8')
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.get_config_path', lambda: config_path)
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.commands.get_workspace_path', lambda _workspace=None: workspace)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {'qq': SimpleNamespace(default_config=lambda: {'enabled': False, 'appId': '', 'secret': '', 'allowFrom': [], 'msgFormat': 'plain'})})
```

### Step 7: Assign runner = CliRunner(...)

```python
runner = CliRunner()
```

### Step 8: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['onboard'], input='n\n')
```

**Verification:**
```python
assert result.exit_code == 0
```

### Step 9: Assign saved = json.loads(...)

```python
saved = json.loads(config_path.read_text(encoding='utf-8'))
```

**Verification:**
```python
assert saved['channels']['qq']['msgFormat'] == 'plain'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
from types import SimpleNamespace
config_path = tmp_path / 'config.json'
workspace = tmp_path / 'workspace'
config_path.write_text(json.dumps({'channels': {'qq': {'enabled': False, 'appId': '', 'secret': '', 'allowFrom': []}}}), encoding='utf-8')
monkeypatch.setattr('nanobot.config.loader.get_config_path', lambda: config_path)
monkeypatch.setattr('nanobot.cli.commands.get_workspace_path', lambda _workspace=None: workspace)
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {'qq': SimpleNamespace(default_config=lambda: {'enabled': False, 'appId': '', 'secret': '', 'allowFrom': [], 'msgFormat': 'plain'})})
from typer.testing import CliRunner
from nanobot.cli.commands import app
runner = CliRunner()
result = runner.invoke(app, ['onboard'], input='n\n')
assert result.exit_code == 0
saved = json.loads(config_path.read_text(encoding='utf-8'))
assert saved['channels']['qq']['msgFormat'] == 'plain'
```

## Next Steps


---

*Source: test_config_migration.py:83 | Complexity: Advanced | Last updated: 2026-04-12*