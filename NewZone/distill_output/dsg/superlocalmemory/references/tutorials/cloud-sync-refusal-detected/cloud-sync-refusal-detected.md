# How To: Cloud Sync Refusal Detected

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test cloud sync refusal detected

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `pathlib`
- `superlocalmemory.cli`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign dc = _imports(...)

```python
dc = _imports()
```

**Verification:**
```python
assert cloud is not None
```

### Step 2: Assign bad = value

```python
bad = tmp_path / 'Dropbox' / 'slm'
```

**Verification:**
```python
assert cloud['status'] == 'error'
```

### Step 3: Call bad.mkdir()

```python
bad.mkdir(parents=True)
```

**Verification:**
```python
assert report['exit_code'] != 0
```

### Step 4: Assign report = dc.run_checks(...)

```python
report = dc.run_checks(data_dir=bad)
```

### Step 5: Assign cloud = next(...)

```python
cloud = next((c for c in report['checks'] if c['name'] == 'data directory'), None)
```

**Verification:**
```python
assert cloud is not None
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
dc = _imports()
bad = tmp_path / 'Dropbox' / 'slm'
bad.mkdir(parents=True)
report = dc.run_checks(data_dir=bad)
cloud = next((c for c in report['checks'] if c['name'] == 'data directory'), None)
assert cloud is not None
assert cloud['status'] == 'error'
assert report['exit_code'] != 0
```

## Next Steps


---

*Source: test_doctor.py:52 | Complexity: Intermediate | Last updated: 2026-05-05*