# How To: Gateway Uses Configured Port When Cli Flag Is Missing

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test gateway uses configured port when cli flag is missing

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
assert 'port 18791' in result.stdout
```

### Step 3: Call config_file.write_text()

```python
config_file.write_text('{}')
```

### Step 4: Assign config = Config(...)

```python
config = Config()
```

### Step 5: Assign config.gateway.port = 18791

```python
config.gateway.port = 18791
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
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: (_ for _ in ()).throw(_StopGatewayError('stop')))
```

### Step 10: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
```

**Verification:**
```python
assert isinstance(result.exception, _StopGatewayError)
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
config.gateway.port = 18791
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: (_ for _ in ()).throw(_StopGatewayError('stop')))
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert 'port 18791' in result.stdout
```

## Next Steps


---

*Source: test_commands.py:858 | Complexity: Advanced | Last updated: 2026-04-12*