# How To: Ram Reservation Timeout Raises

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Second acquisition while the first is held must time out.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `signal`
- `subprocess`
- `sys`
- `textwrap`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: tmp_lock
```

## Step-by-Step Guide

### Step 1: 'Second acquisition while the first is held must time out.'

```python
'Second acquisition while the first is held must time out.'
```

**Verification:**
```python
assert ready_flag.exists(), 'holder never acquired'
```

### Step 2: Assign ready_flag = value

```python
ready_flag = tmp_lock.parent / 'holder_ready'
```

### Step 3: Assign release_flag = value

```python
release_flag = tmp_lock.parent / 'holder_release'
```

### Step 4: Assign holder_script = textwrap.dedent(...)

```python
holder_script = textwrap.dedent(f"\n        import sys, time\n        from pathlib import Path\n        sys.path.insert(0, {str(Path(__file__).resolve().parents[2] / 'src')!r})\n        from superlocalmemory.core import ram_lock as rl\n        rl.RAM_LOCK_PATH = Path({str(tmp_lock)!r})\n        with rl.ram_reservation('holder', required_mb=1, timeout_s=10.0):\n            Path({str(ready_flag)!r}).write_text('ok')\n            deadline = time.time() + 15\n            while time.time() < deadline:\n                if Path({str(release_flag)!r}).exists():\n                    break\n                time.sleep(0.05)\n    ")
```

### Step 5: Assign proc = subprocess.Popen(...)

```python
proc = subprocess.Popen([sys.executable, '-c', holder_script])
```

### Step 6: Assign t0 = time.time(...)

```python
t0 = time.time()
```

**Verification:**
```python
assert ready_flag.exists(), 'holder never acquired'
```

### Step 7: Call release_flag.write_text()

```python
release_flag.write_text('go')
```

### Step 8: Call time.sleep()

```python
time.sleep(0.05)
```

### Step 9: Call proc.wait()

```python
proc.wait(timeout=10)
```

### Step 10: Call pytest.fail()

```python
pytest.fail('should not enter body')
```

### Step 11: Call proc.kill()

```python
proc.kill()
```

### Step 12: Call proc.wait()

```python
proc.wait(timeout=5)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_lock

# Workflow
'Second acquisition while the first is held must time out.'
from superlocalmemory.core import ram_lock
ready_flag = tmp_lock.parent / 'holder_ready'
release_flag = tmp_lock.parent / 'holder_release'
holder_script = textwrap.dedent(f"\n        import sys, time\n        from pathlib import Path\n        sys.path.insert(0, {str(Path(__file__).resolve().parents[2] / 'src')!r})\n        from superlocalmemory.core import ram_lock as rl\n        rl.RAM_LOCK_PATH = Path({str(tmp_lock)!r})\n        with rl.ram_reservation('holder', required_mb=1, timeout_s=10.0):\n            Path({str(ready_flag)!r}).write_text('ok')\n            deadline = time.time() + 15\n            while time.time() < deadline:\n                if Path({str(release_flag)!r}).exists():\n                    break\n                time.sleep(0.05)\n    ")
proc = subprocess.Popen([sys.executable, '-c', holder_script])
try:
    t0 = time.time()
    while not ready_flag.exists() and time.time() - t0 < 10:
        time.sleep(0.05)
    assert ready_flag.exists(), 'holder never acquired'
    with pytest.raises(RuntimeError, match='timeout'):
        with ram_lock.ram_reservation('waiter', required_mb=1, timeout_s=0.5):
            pytest.fail('should not enter body')
finally:
    release_flag.write_text('go')
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
```

## Next Steps


---

*Source: test_ram_lock.py:68 | Complexity: Advanced | Last updated: 2026-05-05*