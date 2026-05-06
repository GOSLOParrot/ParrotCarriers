# How To: Json Output Shape

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test json output shape

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
assert back == report
```

### Step 2: Assign report = dc.run_checks(...)

```python
report = dc.run_checks(data_dir=tmp_path)
```

### Step 3: Assign blob = json.dumps(...)

```python
blob = json.dumps(report)
```

### Step 4: Assign back = json.loads(...)

```python
back = json.loads(blob)
```

**Verification:**
```python
assert back == report
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
dc = _imports()
report = dc.run_checks(data_dir=tmp_path)
blob = json.dumps(report)
back = json.loads(blob)
assert back == report
```

## Next Steps


---

*Source: test_doctor.py:44 | Complexity: Intermediate | Last updated: 2026-05-05*