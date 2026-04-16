# How To: Gateway Uses Workspace Directory For Cron Store

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test gateway uses workspace directory for cron store

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
assert seen['cron_store'] == config.workspace_path / 'cron' / 'jobs.json'
```

### Step 3: Call config_file.write_text()

```python
config_file.write_text('{}')
```

### Step 4: Assign config = Config(...)

```python
config = Config()
```

### Step 5: Assign config.agents.defaults.workspace = str(...)

```python
config.agents.defaults.workspace = str(tmp_path / 'config-workspace')
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
```

### Step 7: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
```

### Step 8: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
```

### Step 9: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
```

### Step 10: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
```

### Step 11: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())
```

### Step 12: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
```

### Step 13: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
```

**Verification:**
```python
assert isinstance(result.exception, _StopGatewayError)
```

### Step 14: Assign unknown = store_path

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
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'config-workspace')
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())

class _StopCron:

    def __init__(self, store_path: Path) -> None:
        seen['cron_store'] = store_path
        raise _StopGatewayError('stop')
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['cron_store'] == config.workspace_path / 'cron' / 'jobs.json'
```

## Next Steps


---

*Source: test_commands.py:706 | Complexity: Advanced | Last updated: 2026-04-12*