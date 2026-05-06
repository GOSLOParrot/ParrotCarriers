# How To: Custom Profile Writes Config Toml

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Custom mode with an explicit reply-file JSON must write
`~/.superlocalmemory/config.toml` with the custom values. Uses
--reply-file so the test doesn't need a real TTY.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `re`
- `shutil`
- `subprocess`
- `pathlib`
- `pytest`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: "Custom mode with an explicit reply-file JSON must write\n    `~/.superlocalmemory/config.toml` with the custom values. Uses\n    --reply-file so the test doesn't need a real TTY.\n    "

```python
"Custom mode with an explicit reply-file JSON must write\n    `~/.superlocalmemory/config.toml` with the custom values. Uses\n    --reply-file so the test doesn't need a real TTY.\n    "
```

**Verification:**
```python
assert result.returncode == 0, f'custom profile write failed: stdout={result.stdout} stderr={result.stderr}'
```

### Step 2: Assign home = value

```python
home = tmp_path / 'home'
```

**Verification:**
```python
assert cfg.exists(), f'expected config.toml at {cfg}, stdout={result.stdout}'
```

### Step 3: Call home.mkdir()

```python
home.mkdir()
```

**Verification:**
```python
assert parsed.get('profile') == 'custom', f'bad toml: {parsed}'
```

### Step 4: Assign reply_file = value

```python
reply_file = tmp_path / 'replies.json'
```

**Verification:**
```python
assert parsed.get('runtime', {}).get('ram_ceiling_mb') == 1500, f'ram_ceiling_mb not persisted: {parsed}'
```

### Step 5: Call reply_file.write_text()

```python
reply_file.write_text(json.dumps({'profile': 'custom', 'ram_ceiling_mb': 1500, 'hot_path_hooks': 'sync_async', 'reranker': 'onnx_int8_l6', 'context_injection_tokens': 500, 'skill_evolution_enabled': False, 'evolution_llm': 'haiku', 'online_retrain_cadence': '50_outcomes', 'consolidation_cadence': '6h_nightly'}))
```

### Step 6: Assign result = _run(...)

```python
result = _run([f'--home={home}', '--home-outside-home', '--profile=custom', f'--reply-file={reply_file}'])
```

**Verification:**
```python
assert result.returncode == 0, f'custom profile write failed: stdout={result.stdout} stderr={result.stderr}'
```

### Step 7: Assign cfg = value

```python
cfg = home / '.superlocalmemory' / 'config.toml'
```

**Verification:**
```python
assert cfg.exists(), f'expected config.toml at {cfg}, stdout={result.stdout}'
```

### Step 8: Assign parsed = _read_toml_kv(...)

```python
parsed = _read_toml_kv(cfg)
```

**Verification:**
```python
assert parsed.get('profile') == 'custom', f'bad toml: {parsed}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
"Custom mode with an explicit reply-file JSON must write\n    `~/.superlocalmemory/config.toml` with the custom values. Uses\n    --reply-file so the test doesn't need a real TTY.\n    "
home = tmp_path / 'home'
home.mkdir()
reply_file = tmp_path / 'replies.json'
reply_file.write_text(json.dumps({'profile': 'custom', 'ram_ceiling_mb': 1500, 'hot_path_hooks': 'sync_async', 'reranker': 'onnx_int8_l6', 'context_injection_tokens': 500, 'skill_evolution_enabled': False, 'evolution_llm': 'haiku', 'online_retrain_cadence': '50_outcomes', 'consolidation_cadence': '6h_nightly'}))
result = _run([f'--home={home}', '--home-outside-home', '--profile=custom', f'--reply-file={reply_file}'])
assert result.returncode == 0, f'custom profile write failed: stdout={result.stdout} stderr={result.stderr}'
cfg = home / '.superlocalmemory' / 'config.toml'
assert cfg.exists(), f'expected config.toml at {cfg}, stdout={result.stdout}'
parsed = _read_toml_kv(cfg)
assert parsed.get('profile') == 'custom', f'bad toml: {parsed}'
assert parsed.get('runtime', {}).get('ram_ceiling_mb') == 1500, f'ram_ceiling_mb not persisted: {parsed}'
```

## Next Steps


---

*Source: test_interactive_installer.py:160 | Complexity: Advanced | Last updated: 2026-05-05*