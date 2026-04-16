# How To: Save Config Writes Context Window Tokens But Not Memory Window

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test save config writes context window tokens but not memory window

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert defaults['maxTokens'] == 2222
```

### Step 2: Call config_path.write_text()

```python
config_path.write_text(json.dumps({'agents': {'defaults': {'maxTokens': 2222, 'memoryWindow': 30}}}), encoding='utf-8')
```

**Verification:**
```python
assert defaults['contextWindowTokens'] == 65536
```

### Step 3: Assign config = load_config(...)

```python
config = load_config(config_path)
```

**Verification:**
```python
assert 'memoryWindow' not in defaults
```

### Step 4: Call save_config()

```python
save_config(config, config_path)
```

### Step 5: Assign saved = json.loads(...)

```python
saved = json.loads(config_path.read_text(encoding='utf-8'))
```

### Step 6: Assign defaults = value

```python
defaults = saved['agents']['defaults']
```

**Verification:**
```python
assert defaults['maxTokens'] == 2222
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
config_path = tmp_path / 'config.json'
config_path.write_text(json.dumps({'agents': {'defaults': {'maxTokens': 2222, 'memoryWindow': 30}}}), encoding='utf-8')
config = load_config(config_path)
save_config(config, config_path)
saved = json.loads(config_path.read_text(encoding='utf-8'))
defaults = saved['agents']['defaults']
assert defaults['maxTokens'] == 2222
assert defaults['contextWindowTokens'] == 65536
assert 'memoryWindow' not in defaults
```

## Next Steps


---

*Source: test_config_migration.py:29 | Complexity: Intermediate | Last updated: 2026-04-12*