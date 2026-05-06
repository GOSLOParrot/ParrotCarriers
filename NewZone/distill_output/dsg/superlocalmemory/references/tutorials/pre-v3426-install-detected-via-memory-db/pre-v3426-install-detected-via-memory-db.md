# How To: Pre V3426 Install Detected Via Memory Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: marker absent but memory.db present = pre-v3.4.26 user upgrading.
Banner should emit with 'from an earlier version'.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.cli.version_banner`
- `os`
- `sys`
- `os`
- `sys`

**Setup Required:**
```python
# Fixtures: slm_home, capsys
```

## Step-by-Step Guide

### Step 1: "marker absent but memory.db present = pre-v3.4.26 user upgrading.\n        Banner should emit with 'from an earlier version'."

```python
"marker absent but memory.db present = pre-v3.4.26 user upgrading.\n        Banner should emit with 'from an earlier version'."
```

**Verification:**
```python
assert emitted is True
```

### Step 2: Call unknown.write_bytes()

```python
(slm_home / 'memory.db').write_bytes(b'SQLite format 3\x00')
```

**Verification:**
```python
assert '3.4.26' in captured.out
```

### Step 3: Assign emitted = check_and_emit_upgrade_banner(...)

```python
emitted = check_and_emit_upgrade_banner(current='3.4.26')
```

**Verification:**
```python
assert read_marker_version() == '3.4.26'
```

### Step 4: Assign captured = capsys.readouterr(...)

```python
captured = capsys.readouterr()
```

**Verification:**
```python
assert emitted2 is False
```

### Step 5: Assign emitted2 = check_and_emit_upgrade_banner(...)

```python
emitted2 = check_and_emit_upgrade_banner(current='3.4.26')
```

**Verification:**
```python
assert captured2.out == ''
```

### Step 6: Assign captured2 = capsys.readouterr(...)

```python
captured2 = capsys.readouterr()
```

**Verification:**
```python
assert emitted2 is False
```


## Complete Example

```python
# Setup
# Fixtures: slm_home, capsys

# Workflow
"marker absent but memory.db present = pre-v3.4.26 user upgrading.\n        Banner should emit with 'from an earlier version'."
(slm_home / 'memory.db').write_bytes(b'SQLite format 3\x00')
emitted = check_and_emit_upgrade_banner(current='3.4.26')
captured = capsys.readouterr()
assert emitted is True
assert '3.4.26' in captured.out
assert read_marker_version() == '3.4.26'
emitted2 = check_and_emit_upgrade_banner(current='3.4.26')
captured2 = capsys.readouterr()
assert emitted2 is False
assert captured2.out == ''
```

## Next Steps


---

*Source: test_version_banner.py:52 | Complexity: Intermediate | Last updated: 2026-05-05*