# How To: Config Save And Reload

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test config save and reload

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pytest`
- `pathlib`
- `unittest.mock`
- `superlocalmemory.llm.backbone`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign config = SLMConfig.for_mode(...)

```python
config = SLMConfig.for_mode(Mode.C, llm_provider='openrouter', llm_model='openai/gpt-4.1-mini', llm_api_key='sk-or-test123', llm_api_base='https://openrouter.ai/api/v1')
```

**Verification:**
```python
assert config_path.exists()
```

### Step 2: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert data['mode'] == 'c'
```

### Step 3: Call config.save()

```python
config.save(config_path)
```

**Verification:**
```python
assert data['llm']['provider'] == 'openrouter'
```

### Step 4: Assign data = json.loads(...)

```python
data = json.loads(config_path.read_text())
```

**Verification:**
```python
assert reloaded.mode == Mode.C
```

### Step 5: Assign reloaded = SLMConfig.load(...)

```python
reloaded = SLMConfig.load(config_path)
```

**Verification:**
```python
assert reloaded.llm.provider == 'openrouter'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
config = SLMConfig.for_mode(Mode.C, llm_provider='openrouter', llm_model='openai/gpt-4.1-mini', llm_api_key='sk-or-test123', llm_api_base='https://openrouter.ai/api/v1')
config_path = tmp_path / 'config.json'
config.save(config_path)
assert config_path.exists()
data = json.loads(config_path.read_text())
assert data['mode'] == 'c'
assert data['llm']['provider'] == 'openrouter'
reloaded = SLMConfig.load(config_path)
assert reloaded.mode == Mode.C
assert reloaded.llm.provider == 'openrouter'
assert reloaded.llm.model == 'openai/gpt-4.1-mini'
```

## Next Steps


---

*Source: test_llm_provider.py:66 | Complexity: Intermediate | Last updated: 2026-05-05*