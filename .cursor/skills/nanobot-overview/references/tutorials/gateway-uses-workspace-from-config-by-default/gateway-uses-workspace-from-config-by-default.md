# How To: Gateway Uses Workspace From Config By Default

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test gateway uses workspace from config by default

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
assert seen['config_path'] == config_file.resolve()
```

### Step 3: Call config_file.write_text()

```python
config_file.write_text('{}')
```

**Verification:**
```python
assert seen['workspace'] == Path(config.agents.defaults.workspace)
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
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda path: seen.__setitem__('config_path', path))
```

### Step 7: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
```

### Step 8: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda path: seen.__setitem__('workspace', path))
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
config.agents.defaults.workspace = str(tmp_path / 'config-workspace')
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda path: seen.__setitem__('config_path', path))
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda path: seen.__setitem__('workspace', path))
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: (_ for _ in ()).throw(_StopGatewayError('stop')))
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['config_path'] == config_file.resolve()
assert seen['workspace'] == Path(config.agents.defaults.workspace)
```

## Next Steps


---

*Source: test_commands.py:645 | Complexity: Advanced | Last updated: 2026-04-12*