# How To: Postinstall Aborts On Sha Mismatch

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: H12: postinstall computes SHA256 of a downloaded file and MUST
compare against the manifest. We simulate the comparison in-process
by calling sha256File on a file whose SHA differs from the claimed
one.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `shutil`
- `stat`
- `subprocess`
- `sys`
- `textwrap`
- `pathlib`
- `pytest`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'H12: postinstall computes SHA256 of a downloaded file and MUST\n    compare against the manifest. We simulate the comparison in-process\n    by calling sha256File on a file whose SHA differs from the claimed\n    one.'

```python
'H12: postinstall computes SHA256 of a downloaded file and MUST\n    compare against the manifest. We simulate the comparison in-process\n    by calling sha256File on a file whose SHA differs from the claimed\n    one.'
```

**Verification:**
```python
assert proc.returncode == 0
```

### Step 2: Assign script = value

```python
script = REPO_ROOT / 'scripts' / 'postinstall_binary.js'
```

**Verification:**
```python
assert 'MISMATCH_OK' in proc.stdout
```

### Step 3: Assign asset = value

```python
asset = tmp_path / 'fake.bin'
```

### Step 4: Call asset.write_bytes()

```python
asset.write_bytes(b'hello')
```

### Step 5: Assign probe = value

```python
probe = tmp_path / 'probe.js'
```

### Step 6: Call probe.write_text()

```python
probe.write_text(textwrap.dedent(f"        const m = require({str(script)!r});\n        (async () => {{\n            const got = await m.sha256File({str(asset)!r});\n            const claimed = '0'.repeat(64);\n            if (got === claimed) {{\n                console.error('unexpectedly matched');\n                process.exit(2);\n            }}\n            console.log('MISMATCH_OK');\n        }})();\n    "))
```

### Step 7: Assign proc = subprocess.run(...)

```python
proc = subprocess.run(['node', str(probe)], capture_output=True, text=True, timeout=15)
```

**Verification:**
```python
assert proc.returncode == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'H12: postinstall computes SHA256 of a downloaded file and MUST\n    compare against the manifest. We simulate the comparison in-process\n    by calling sha256File on a file whose SHA differs from the claimed\n    one.'
script = REPO_ROOT / 'scripts' / 'postinstall_binary.js'
asset = tmp_path / 'fake.bin'
asset.write_bytes(b'hello')
probe = tmp_path / 'probe.js'
probe.write_text(textwrap.dedent(f"        const m = require({str(script)!r});\n        (async () => {{\n            const got = await m.sha256File({str(asset)!r});\n            const claimed = '0'.repeat(64);\n            if (got === claimed) {{\n                console.error('unexpectedly matched');\n                process.exit(2);\n            }}\n            console.log('MISMATCH_OK');\n        }})();\n    "))
proc = subprocess.run(['node', str(probe)], capture_output=True, text=True, timeout=15)
assert proc.returncode == 0
assert 'MISMATCH_OK' in proc.stdout
```

## Next Steps


---

*Source: test_dispatcher_fallback.py:200 | Complexity: Advanced | Last updated: 2026-05-05*