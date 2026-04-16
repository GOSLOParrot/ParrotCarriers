# How To: Onboard Wizard Preserves Explicit Config In Next Steps

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test onboard wizard preserves explicit config in next steps

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
assert f'nanobot agent -m "Hello!" --config {resolved_config}' in compact_output
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.cli.onboard.run_onboard', lambda initial_config: OnboardResult(config=initial_config, should_save=True))
```

**Verification:**
```python
assert f'nanobot gateway --config {resolved_config}' in compact_output
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {})
```

### Step 5: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['onboard', '--wizard', '--config', str(config_path), '--workspace', str(workspace_path)])
```

**Verification:**
```python
assert result.exit_code == 0
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
assert f'nanobot agent -m "Hello!" --config {resolved_config}' in compact_output
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
config_path = tmp_path / 'instance' / 'config.json'
workspace_path = tmp_path / 'workspace'
from nanobot.cli.onboard import OnboardResult
monkeypatch.setattr('nanobot.cli.onboard.run_onboard', lambda initial_config: OnboardResult(config=initial_config, should_save=True))
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {})
result = runner.invoke(app, ['onboard', '--wizard', '--config', str(config_path), '--workspace', str(workspace_path)])
assert result.exit_code == 0
stripped_output = _strip_ansi(result.stdout)
compact_output = stripped_output.replace('\n', '')
resolved_config = str(config_path.resolve())
assert f'nanobot agent -m "Hello!" --config {resolved_config}' in compact_output
assert f'nanobot gateway --config {resolved_config}' in compact_output
```

## Next Steps


---

*Source: test_commands.py:177 | Complexity: Advanced | Last updated: 2026-04-12*