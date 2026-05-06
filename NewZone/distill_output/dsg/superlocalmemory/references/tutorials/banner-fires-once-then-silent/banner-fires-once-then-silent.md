# How To: Banner Fires Once Then Silent

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test banner fires once then silent

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.cli.version_banner`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`

**Setup Required:**
```python
# Fixtures: v3_4_25_data_dir, capsys
```

## Step-by-Step Guide

### Step 1: Assign first = check_and_emit_upgrade_banner(...)

```python
first = check_and_emit_upgrade_banner('3.4.26')
```

**Verification:**
```python
assert first is True
```

### Step 2: Assign out1 = value

```python
out1 = capsys.readouterr().out
```

**Verification:**
```python
assert '3.4.26' in out1
```

### Step 3: Assign second = check_and_emit_upgrade_banner(...)

```python
second = check_and_emit_upgrade_banner('3.4.26')
```

**Verification:**
```python
assert second is False
```

### Step 4: Assign out2 = value

```python
out2 = capsys.readouterr().out
```

**Verification:**
```python
assert out2 == ''
```


## Complete Example

```python
# Setup
# Fixtures: v3_4_25_data_dir, capsys

# Workflow
from superlocalmemory.cli.version_banner import check_and_emit_upgrade_banner
first = check_and_emit_upgrade_banner('3.4.26')
out1 = capsys.readouterr().out
assert first is True
assert '3.4.26' in out1
second = check_and_emit_upgrade_banner('3.4.26')
out2 = capsys.readouterr().out
assert second is False
assert out2 == ''
```

## Next Steps


---

*Source: test_upgrade_v3_4_25_to_v3_4_26.py:54 | Complexity: Intermediate | Last updated: 2026-05-05*