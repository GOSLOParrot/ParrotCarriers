# How To: Tty Detection Defaults To Balanced For Non Tty

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Non-TTY invocations (CI, `CI=true`, piped stdin) must skip all prompts
and silently apply Balanced defaults. Manifest contract: zero prompts,
zero stderr interaction, exit 0, `profile = "balanced"` written to
`~/.superlocalmemory/config.toml`.

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

### Step 1: 'Non-TTY invocations (CI, `CI=true`, piped stdin) must skip all prompts\n    and silently apply Balanced defaults. Manifest contract: zero prompts,\n    zero stderr interaction, exit 0, `profile = "balanced"` written to\n    `~/.superlocalmemory/config.toml`.\n    '

```python
'Non-TTY invocations (CI, `CI=true`, piped stdin) must skip all prompts\n    and silently apply Balanced defaults. Manifest contract: zero prompts,\n    zero stderr interaction, exit 0, `profile = "balanced"` written to\n    `~/.superlocalmemory/config.toml`.\n    '
```

**Verification:**
```python
assert result.returncode == 0, f'expected exit 0 in non-TTY mode, got {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}'
```

### Step 2: Assign home = value

```python
home = tmp_path / 'home'
```

**Verification:**
```python
assert not stripped.endswith('?'), f'non-TTY path emitted an interactive prompt: {line!r}\nfull stdout:\n{result.stdout}'
```

### Step 3: Call home.mkdir()

```python
home.mkdir()
```

**Verification:**
```python
assert 'balanced' in result.stdout.lower(), f"expected 'balanced' profile selection in stdout:\n{result.stdout}"
```

### Step 4: Assign env = value

```python
env = {'CI': 'true', 'SLM_INSTALL_FREE_RAM_MB': '8192', 'SLM_INSTALL_COLD_START_MS': '150', 'SLM_INSTALL_DISK_FREE_GB': '250'}
```

### Step 5: Assign result = _run(...)

```python
result = _run(['--dry-run', f'--home={home}', '--home-outside-home'], env=env)
```

**Verification:**
```python
assert result.returncode == 0, f'expected exit 0 in non-TTY mode, got {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}'
```

### Step 6: Assign stripped = line.rstrip(...)

```python
stripped = line.rstrip()
```

**Verification:**
```python
assert not stripped.endswith('?'), f'non-TTY path emitted an interactive prompt: {line!r}\nfull stdout:\n{result.stdout}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Non-TTY invocations (CI, `CI=true`, piped stdin) must skip all prompts\n    and silently apply Balanced defaults. Manifest contract: zero prompts,\n    zero stderr interaction, exit 0, `profile = "balanced"` written to\n    `~/.superlocalmemory/config.toml`.\n    '
home = tmp_path / 'home'
home.mkdir()
env = {'CI': 'true', 'SLM_INSTALL_FREE_RAM_MB': '8192', 'SLM_INSTALL_COLD_START_MS': '150', 'SLM_INSTALL_DISK_FREE_GB': '250'}
result = _run(['--dry-run', f'--home={home}', '--home-outside-home'], env=env)
assert result.returncode == 0, f'expected exit 0 in non-TTY mode, got {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}'
for line in result.stdout.splitlines():
    stripped = line.rstrip()
    assert not stripped.endswith('?'), f'non-TTY path emitted an interactive prompt: {line!r}\nfull stdout:\n{result.stdout}'
assert 'balanced' in result.stdout.lower(), f"expected 'balanced' profile selection in stdout:\n{result.stdout}"
```

## Next Steps


---

*Source: test_interactive_installer.py:97 | Complexity: Intermediate | Last updated: 2026-05-05*