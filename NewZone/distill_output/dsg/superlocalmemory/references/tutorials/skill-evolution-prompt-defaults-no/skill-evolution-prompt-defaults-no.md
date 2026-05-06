# How To: Skill Evolution Prompt Defaults No

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Manifest D3: skill_evolution opt-in default OFF. For Balanced/Power
profiles the installer asks, but the default (pressing Enter / non-TTY)
must be `false`.

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

### Step 1: 'Manifest D3: skill_evolution opt-in default OFF. For Balanced/Power\n    profiles the installer asks, but the default (pressing Enter / non-TTY)\n    must be `false`.\n    '

```python
'Manifest D3: skill_evolution opt-in default OFF. For Balanced/Power\n    profiles the installer asks, but the default (pressing Enter / non-TTY)\n    must be `false`.\n    '
```

**Verification:**
```python
assert result.returncode == 0, result.stderr
```

### Step 2: Assign home = value

```python
home = tmp_path / 'home'
```

**Verification:**
```python
assert cfg.exists(), f'config not written: stdout={result.stdout}'
```

### Step 3: Call home.mkdir()

```python
home.mkdir()
```

**Verification:**
```python
assert evo.get('enabled') is False, f'skill evolution must default to false (opt-in), got {evo}'
```

### Step 4: Assign result = _run(...)

```python
result = _run([f'--home={home}', '--home-outside-home', '--profile=balanced'], env={'CI': 'true'})
```

**Verification:**
```python
assert result.returncode == 0, result.stderr
```

### Step 5: Assign cfg = value

```python
cfg = home / '.superlocalmemory' / 'config.toml'
```

**Verification:**
```python
assert cfg.exists(), f'config not written: stdout={result.stdout}'
```

### Step 6: Assign parsed = _read_toml_kv(...)

```python
parsed = _read_toml_kv(cfg)
```

### Step 7: Assign evo = parsed.get(...)

```python
evo = parsed.get('evolution', {})
```

**Verification:**
```python
assert evo.get('enabled') is False, f'skill evolution must default to false (opt-in), got {evo}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Manifest D3: skill_evolution opt-in default OFF. For Balanced/Power\n    profiles the installer asks, but the default (pressing Enter / non-TTY)\n    must be `false`.\n    '
home = tmp_path / 'home'
home.mkdir()
result = _run([f'--home={home}', '--home-outside-home', '--profile=balanced'], env={'CI': 'true'})
assert result.returncode == 0, result.stderr
cfg = home / '.superlocalmemory' / 'config.toml'
assert cfg.exists(), f'config not written: stdout={result.stdout}'
parsed = _read_toml_kv(cfg)
evo = parsed.get('evolution', {})
assert evo.get('enabled') is False, f'skill evolution must default to false (opt-in), got {evo}'
```

## Next Steps


---

*Source: test_interactive_installer.py:241 | Complexity: Intermediate | Last updated: 2026-05-05*