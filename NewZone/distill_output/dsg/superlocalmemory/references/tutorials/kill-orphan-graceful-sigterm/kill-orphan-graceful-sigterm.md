# How To: Kill Orphan Graceful Sigterm

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: SIGTERM kills a cooperative process.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `signal`
- `subprocess`
- `sys`
- `time`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `json`
- `datetime`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `json`
- `datetime`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `json`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'SIGTERM kills a cooperative process.'

```python
'SIGTERM kills a cooperative process.'
```

**Verification:**
```python
assert result['killed'] is True
```

### Step 2: Assign ready_file = value

```python
ready_file = tmp_path / 'ready'
```

**Verification:**
```python
assert result['method'] == 'sigterm'
```

### Step 3: Assign pid_file = value

```python
pid_file = tmp_path / 'child_pid'
```

**Verification:**
```python
assert result['error'] is None
```

### Step 4: Assign launcher = value

```python
launcher = tmp_path / 'launcher.py'
```

### Step 5: Call launcher.write_text()

```python
launcher.write_text(f"""import os, pathlib, subprocess, sys\nproc = subprocess.Popen([sys.executable, '-c', 'import time, pathlib; pathlib.Path(\\"{ready_file}\\").touch(); time.sleep(300)'], start_new_session=True)\npathlib.Path('{pid_file}').write_text(str(proc.pid))\n""")
```

### Step 6: Call subprocess.run()

```python
subprocess.run([sys.executable, str(launcher)], timeout=5, check=True)
```

### Step 7: Assign target_pid = int(...)

```python
target_pid = int(pid_file.read_text().strip())
```

### Step 8: Assign deadline = value

```python
deadline = time.monotonic() + 5.0
```

### Step 9: Assign result = kill_orphan(...)

```python
result = kill_orphan(target_pid, graceful_timeout_seconds=10.0)
```

**Verification:**
```python
assert result['killed'] is True
```

### Step 10: Call time.sleep()

```python
time.sleep(0.1)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'SIGTERM kills a cooperative process.'
from superlocalmemory.infra.process_reaper import kill_orphan
ready_file = tmp_path / 'ready'
pid_file = tmp_path / 'child_pid'
launcher = tmp_path / 'launcher.py'
launcher.write_text(f"""import os, pathlib, subprocess, sys\nproc = subprocess.Popen([sys.executable, '-c', 'import time, pathlib; pathlib.Path(\\"{ready_file}\\").touch(); time.sleep(300)'], start_new_session=True)\npathlib.Path('{pid_file}').write_text(str(proc.pid))\n""")
subprocess.run([sys.executable, str(launcher)], timeout=5, check=True)
target_pid = int(pid_file.read_text().strip())
deadline = time.monotonic() + 5.0
while time.monotonic() < deadline:
    if ready_file.exists():
        break
    time.sleep(0.1)
result = kill_orphan(target_pid, graceful_timeout_seconds=10.0)
assert result['killed'] is True
assert result['method'] == 'sigterm'
assert result['error'] is None
```

## Next Steps


---

*Source: test_process_reaper.py:150 | Complexity: Advanced | Last updated: 2026-05-05*