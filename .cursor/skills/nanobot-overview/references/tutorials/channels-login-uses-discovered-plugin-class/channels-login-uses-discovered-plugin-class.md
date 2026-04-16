# How To: Channels Login Uses Discovered Plugin Class

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test channels login uses discovered plugin class

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `asyncio`
- `types`
- `unittest.mock`
- `pytest`
- `nanobot.bus.events`
- `nanobot.bus.queue`
- `nanobot.channels.base`
- `nanobot.channels.manager`
- `nanobot.config.schema`
- `nanobot.channels.registry`
- `nanobot.channels.registry`
- `nanobot.channels.registry`
- `nanobot.channels.registry`
- `nanobot.channels.registry`
- `nanobot.channels.manager`
- `nanobot.cli.commands`
- `nanobot.config.schema`
- `typer.testing`
- `nanobot.channels.telegram`
- `nanobot.channels.telegram`
- `pydantic`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign runner = CliRunner(...)

```python
runner = CliRunner()
```

**Verification:**
```python
assert result.exit_code == 0
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.config.loader.load_config', lambda: Config())
```

**Verification:**
```python
assert seen['force'] is True
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {'fakeplugin': _LoginPlugin})
```

### Step 4: Assign result = runner.invoke(...)

```python
result = runner.invoke(app, ['channels', 'login', 'fakeplugin', '--force'])
```

**Verification:**
```python
assert result.exit_code == 0
```

### Step 5: Assign display_name = 'Login Plugin'

```python
display_name = 'Login Plugin'
```

### Step 6: Assign unknown = force

```python
seen['force'] = force
```

### Step 7: Assign unknown = value

```python
seen['config'] = self.config
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
from nanobot.cli.commands import app
from nanobot.config.schema import Config
from typer.testing import CliRunner
runner = CliRunner()
seen: dict[str, object] = {}

class _LoginPlugin(_FakePlugin):
    display_name = 'Login Plugin'

    async def login(self, force: bool=False) -> bool:
        seen['force'] = force
        seen['config'] = self.config
        return True
monkeypatch.setattr('nanobot.config.loader.load_config', lambda: Config())
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {'fakeplugin': _LoginPlugin})
result = runner.invoke(app, ['channels', 'login', 'fakeplugin', '--force'])
assert result.exit_code == 0
assert seen['force'] is True
```

## Next Steps


---

*Source: test_channel_plugins.py:195 | Complexity: Advanced | Last updated: 2026-04-12*