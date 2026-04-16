# How To: Gateway Custom Config Workspace Does Not Migrate Legacy Cron

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test gateway custom config workspace does not migrate legacy cron

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
# Fixtures: monkeypatch, tmp_path
```

## Step-by-Step Guide

### Step 1: Assign config_file = value

```python
config_file = tmp_path / 'instance' / 'config.json'
```

**Verification:**
```python
assert isinstance(result.exception, _StopGatewayError)
```

### Step 2: Call config_file.parent.mkdir()

```python
config_file.parent.mkdir(parents=True)
```

**Verification:**
```python
assert seen['cron_store'] == custom_workspace / 'cron' / 'jobs.json'
```

### Step 3: Call config_file.write_text()

```python
config_file.write_text('{}')
```

**Verification:**
```python
assert legacy_file.exists()
```

### Step 4: Assign legacy_dir = value

```python
legacy_dir = tmp_path / 'global' / 'cron'
```

**Verification:**
```python
assert not (custom_workspace / 'cron' / 'jobs.json').exists()
```

### Step 5: Call legacy_dir.mkdir()

```python
legacy_dir.mkdir(parents=True)
```

### Step 6: Assign legacy_file = value

```python
legacy_file = legacy_dir / 'jobs.json'
```

### Step 7: Call legacy_file.write_text()

```python
legacy_file.write_text('{"jobs": []}')
```

### Step 8: Assign custom_workspace = value

```python
custom_workspace = tmp_path / 'custom-workspace'
```

### Step 9: Assign config = Config(...)

```python
config = Config()
```

### Step 10: Assign config.agents.defaults.workspace = str(...)

```python
config.agents.defaults.workspace = str(custom_workspace)
```

### Step 11: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
```

### Step 12: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
```

### Step 13: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
```

### Step 14: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
```

### Step 15: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
```

### Step 16: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())
```

### Step 17: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.paths.get_cron_dir', lambda: legacy_dir)
```

### Step 18: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
```

### Step 19: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
```

**Verification:**
```python
assert isinstance(result.exception, _StopGatewayError)
```

### Step 20: Assign unknown = store_path

```python
seen['cron_store'] = store_path
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch, tmp_path

# Workflow
config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
legacy_file = legacy_dir / 'jobs.json'
legacy_file.write_text('{"jobs": []}')
custom_workspace = tmp_path / 'custom-workspace'
config = Config()
config.agents.defaults.workspace = str(custom_workspace)
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())
monkeypatch.setattr('nanobot.config.paths.get_cron_dir', lambda: legacy_dir)

class _StopCron:

    def __init__(self, store_path: Path) -> None:
        seen['cron_store'] = store_path
        raise _StopGatewayError('stop')
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['cron_store'] == custom_workspace / 'cron' / 'jobs.json'
assert legacy_file.exists()
assert not (custom_workspace / 'cron' / 'jobs.json').exists()
```

## Next Steps


---

*Source: test_commands.py:777 | Complexity: Advanced | Last updated: 2026-04-12*