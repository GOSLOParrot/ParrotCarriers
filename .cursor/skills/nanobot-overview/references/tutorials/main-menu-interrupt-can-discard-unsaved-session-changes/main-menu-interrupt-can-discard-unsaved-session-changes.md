# How To: Main Menu Interrupt Can Discard Unsaved Session Changes

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test main menu interrupt can discard unsaved session changes

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
- `types`
- `typing`
- `pytest`
- `pydantic`
- `nanobot.cli`
- `nanobot.cli.commands`
- `nanobot.cli.onboard`
- `nanobot.config.schema`
- `nanobot.utils.helpers`
- `nanobot.cli.onboard`
- `nanobot.cli.onboard`
- `nanobot.cli.onboard`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign initial_config = Config(...)

```python
initial_config = Config()
```

**Verification:**
```python
assert result.should_save is False
```

### Step 2: Assign responses = iter(...)

```python
responses = iter(['[A] Agent Settings', KeyboardInterrupt(), '[X] Exit Without Saving'])
```

**Verification:**
```python
assert result.config.model_dump(by_alias=True) == initial_config.model_dump(by_alias=True)
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(onboard_wizard, '_show_main_menu_header', lambda: None)
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(onboard_wizard, 'questionary', SimpleNamespace(select=fake_select))
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(onboard_wizard, '_configure_general_settings', fake_configure_general_settings)
```

### Step 6: Assign result = run_onboard(...)

```python
result = run_onboard(initial_config=initial_config)
```

**Verification:**
```python
assert result.should_save is False
```

### Step 7: Assign self.response = response

```python
self.response = response
```

### Step 8: Assign config.agents.defaults.model = 'test/provider-model'

```python
config.agents.defaults.model = 'test/provider-model'
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
initial_config = Config()
responses = iter(['[A] Agent Settings', KeyboardInterrupt(), '[X] Exit Without Saving'])

class FakePrompt:

    def __init__(self, response):
        self.response = response

    def ask(self):
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response

def fake_select(*_args, **_kwargs):
    return FakePrompt(next(responses))

def fake_configure_general_settings(config, section):
    if section == 'Agent Settings':
        config.agents.defaults.model = 'test/provider-model'
monkeypatch.setattr(onboard_wizard, '_show_main_menu_header', lambda: None)
monkeypatch.setattr(onboard_wizard, 'questionary', SimpleNamespace(select=fake_select))
monkeypatch.setattr(onboard_wizard, '_configure_general_settings', fake_configure_general_settings)
result = run_onboard(initial_config=initial_config)
assert result.should_save is False
assert result.config.model_dump(by_alias=True) == initial_config.model_dump(by_alias=True)
```

## Next Steps


---

*Source: test_onboard_logic.py:461 | Complexity: Advanced | Last updated: 2026-04-12*