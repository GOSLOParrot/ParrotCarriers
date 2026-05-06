# How To: Write Manifest Emits Json And Sig

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test write manifest emits json and sig

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `pathlib`
- `pytest`
- `release_manifest`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign assets_dir = value

```python
assets_dir = tmp_path / 'assets'
```

**Verification:**
```python
assert manifest_path.is_file()
```

### Step 2: Call assets_dir.mkdir()

```python
assets_dir.mkdir()
```

**Verification:**
```python
assert sig_path.is_file()
```

### Step 3: Assign manifest = rm.build_manifest(...)

```python
manifest = rm.build_manifest('3.4.22', [rm.AssetSpec(path=_seed_asset(assets_dir, 'slm-hook-linux-arm64.tar.gz', b'linux-arm'), platform='linux', arch='arm64', signing=rm.SIGNING_UNSIGNED)], released_at='2026-04-17T00:00:00+00:00')
```

**Verification:**
```python
assert loaded['version'] == '3.4.22'
```

### Step 4: Assign out_dir = value

```python
out_dir = tmp_path / 'release'
```

**Verification:**
```python
assert 'placeholder' in sig_body
```

### Step 5: Assign unknown = rm.write_manifest(...)

```python
manifest_path, sig_path = rm.write_manifest(manifest, out_dir)
```

**Verification:**
```python
assert manifest.manifest_sha256_self in sig_body
```

### Step 6: Assign loaded = json.loads(...)

```python
loaded = json.loads(manifest_path.read_text(encoding='utf-8'))
```

**Verification:**
```python
assert loaded['version'] == '3.4.22'
```

### Step 7: Assign sig_body = sig_path.read_text(...)

```python
sig_body = sig_path.read_text(encoding='utf-8')
```

**Verification:**
```python
assert 'placeholder' in sig_body
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
assets_dir = tmp_path / 'assets'
assets_dir.mkdir()
manifest = rm.build_manifest('3.4.22', [rm.AssetSpec(path=_seed_asset(assets_dir, 'slm-hook-linux-arm64.tar.gz', b'linux-arm'), platform='linux', arch='arm64', signing=rm.SIGNING_UNSIGNED)], released_at='2026-04-17T00:00:00+00:00')
out_dir = tmp_path / 'release'
manifest_path, sig_path = rm.write_manifest(manifest, out_dir)
assert manifest_path.is_file()
assert sig_path.is_file()
loaded = json.loads(manifest_path.read_text(encoding='utf-8'))
assert loaded['version'] == '3.4.22'
sig_body = sig_path.read_text(encoding='utf-8')
assert 'placeholder' in sig_body
assert manifest.manifest_sha256_self in sig_body
```

## Next Steps


---

*Source: test_manifest_generator.py:169 | Complexity: Intermediate | Last updated: 2026-05-05*