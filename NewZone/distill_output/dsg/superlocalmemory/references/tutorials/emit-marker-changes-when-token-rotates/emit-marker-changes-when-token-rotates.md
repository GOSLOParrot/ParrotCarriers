# How To: Emit Marker Changes When Token Rotates

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Rotating the install token invalidates old markers — by design.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `secrets`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Rotating the install token invalidates old markers — by design.'

```python
'Rotating the install token invalidates old markers — by design.'
```

**Verification:**
```python
assert m1 != m2
```

### Step 2: Assign tok1 = value

```python
tok1 = tmp_path / 't1'
```

### Step 3: Call tok1.write_text()

```python
tok1.write_text('a' * 64, encoding='utf-8')
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(sp, '_install_token_path', lambda: tok1)
```

### Step 5: Assign m1 = rp._emit_marker(...)

```python
m1 = rp._emit_marker('fact_xyz')
```

### Step 6: Assign tok2 = value

```python
tok2 = tmp_path / 't2'
```

### Step 7: Call tok2.write_text()

```python
tok2.write_text('b' * 64, encoding='utf-8')
```

### Step 8: Call monkeypatch.setattr()

```python
monkeypatch.setattr(sp, '_install_token_path', lambda: tok2)
```

### Step 9: Assign m2 = rp._emit_marker(...)

```python
m2 = rp._emit_marker('fact_xyz')
```

**Verification:**
```python
assert m1 != m2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Rotating the install token invalidates old markers — by design.'
tok1 = tmp_path / 't1'
tok1.write_text('a' * 64, encoding='utf-8')
monkeypatch.setattr(sp, '_install_token_path', lambda: tok1)
m1 = rp._emit_marker('fact_xyz')
tok2 = tmp_path / 't2'
tok2.write_text('b' * 64, encoding='utf-8')
monkeypatch.setattr(sp, '_install_token_path', lambda: tok2)
m2 = rp._emit_marker('fact_xyz')
assert m1 != m2
```

## Next Steps


---

*Source: test_recall_markers.py:68 | Complexity: Advanced | Last updated: 2026-05-05*