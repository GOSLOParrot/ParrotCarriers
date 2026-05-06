# How To: Report Flags Missing Migration Marker

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test report flags missing migration marker

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
assert 'v3.4.26 migration' in names
```

### Step 2: Assign report = dc.run_checks(...)

```python
report = dc.run_checks(data_dir=tmp_path)
```

**Verification:**
```python
assert migration['status'] == 'warn'
```

### Step 3: Assign names = value

```python
names = {c['name'] for c in report['checks']}
```

**Verification:**
```python
assert 'v3.4.26 migration' in names
```

### Step 4: Assign migration = next(...)

```python
migration = next((c for c in report['checks'] if c['name'] == 'v3.4.26 migration'))
```

**Verification:**
```python
assert migration['status'] == 'warn'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
dc = _imports()
report = dc.run_checks(data_dir=tmp_path)
names = {c['name'] for c in report['checks']}
assert 'v3.4.26 migration' in names
migration = next((c for c in report['checks'] if c['name'] == 'v3.4.26 migration'))
assert migration['status'] == 'warn'
```

## Next Steps


---

*Source: test_doctor.py:26 | Complexity: Intermediate | Last updated: 2026-05-05*