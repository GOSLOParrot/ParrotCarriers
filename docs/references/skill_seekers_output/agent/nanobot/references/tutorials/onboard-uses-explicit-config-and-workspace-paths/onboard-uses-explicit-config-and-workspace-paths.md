# How To: Onboard Uses Explicit Config And Workspace Paths

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test onboard uses explicit config and workspace paths

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
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign config_path = value

```python
config_path = tmp_path / 'instance' / 'config.json'
```

**Verification:**
```python
assert result.exit_code == 0
```

### Step 2: Assign workspace_path = value

```python
workspace_path = tmp_path / 'workspace'
```

**Verification:**
```python
assert saved.workspace_path == workspace_path
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {})
```

**Verification:**
```python
assert (workspace_path / 'AGENTS.md').exists()
```

### Step 4: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['onboard', '--config', str(config_path), '--workspace', str(workspace_path)])
```

**Verification:**
```python
assert resolved_config in compact_output
```

### Step 5: Assign saved = Config.model_validate(...)

```python
saved = Config.model_validate(json.loads(config_path.read_text(encoding='utf-8')))
```

**Verification:**
```python
assert f'--config {resolved_config}' in compact_output
```

### Step 6: Assign stripped_output = _strip_ansi(...)

```python
stripped_output = _strip_ansi(result.stdout)
```

### Step 7: Assign compact_output = stripped_output.replace(...)

```python
compact_output = stripped_output.replace('\n', '')
```

### Step 8: Assign resolved_config = str(...)

```python
resolved_config = str(config_path.resolve())
```

**Verification:**
```python
assert resolved_config in compact_output
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
config_path = tmp_path / 'instance' / 'config.json'
workspace_path = tmp_path / 'workspace'
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {})
result = runner.invoke(app, ['onboard', '--config', str(config_path), '--workspace', str(workspace_path)])
assert result.exit_code == 0
saved = Config.model_validate(json.loads(config_path.read_text(encoding='utf-8')))
assert saved.workspace_path == workspace_path
assert (workspace_path / 'AGENTS.md').exists()
stripped_output = _strip_ansi(result.stdout)
compact_output = stripped_output.replace('\n', '')
resolved_config = str(config_path.resolve())
assert resolved_config in compact_output
assert f'--config {resolved_config}' in compact_output
```

## Next Steps


---

*Source: test_commands.py:155 | Complexity: Advanced | Last updated: 2026-04-12*