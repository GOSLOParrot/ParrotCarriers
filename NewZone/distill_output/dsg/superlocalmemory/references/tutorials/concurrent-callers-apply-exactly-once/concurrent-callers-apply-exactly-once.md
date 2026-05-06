# How To: Concurrent Callers Apply Exactly Once

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test concurrent callers apply exactly once

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`
- `threading`
- `superlocalmemory.migrations.v3_4_25_to_v3_4_26`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Call monkeypatch.setattr()

```python
monkeypatch.setattr(mod, '_daemon_running', lambda: False)
```

**Verification:**
```python
assert call_count['n'] == 1, f"migrate() ran {call_count['n']}x instead of exactly once"
```

### Step 2: Assign call_count = value

```python
call_count = {'n': 0}
```

**Verification:**
```python
assert statuses.count('applied') == 1
```

### Step 3: Assign original_migrate = value

```python
original_migrate = mod.migrate
```

**Verification:**
```python
assert s in ('applied', 'already_applied', 'deferred'), s
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(mod, 'migrate', _counting_migrate)
```

### Step 5: Assign status_lock = threading.Lock(...)

```python
status_lock = threading.Lock()
```

### Step 6: Assign threads = value

```python
threads = [threading.Thread(target=_call) for _ in range(8)]
```

**Verification:**
```python
assert call_count['n'] == 1, f"migrate() ran {call_count['n']}x instead of exactly once"
```

### Step 7: Assign res = mod.migrate_if_safe(...)

```python
res = mod.migrate_if_safe(tmp_path)
```

### Step 8: Call t.start()

```python
t.start()
```

### Step 9: Call t.join()

```python
t.join()
```

**Verification:**
```python
assert s in ('applied', 'already_applied', 'deferred'), s
```

### Step 10: Call statuses.append()

```python
statuses.append(res['status'])
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
import threading
import superlocalmemory.migrations.v3_4_25_to_v3_4_26 as mod
monkeypatch.setattr(mod, '_daemon_running', lambda: False)
call_count = {'n': 0}
original_migrate = mod.migrate

def _counting_migrate(data_dir):
    call_count['n'] += 1
    return original_migrate(data_dir)
monkeypatch.setattr(mod, 'migrate', _counting_migrate)
statuses: list[str] = []
status_lock = threading.Lock()

def _call():
    res = mod.migrate_if_safe(tmp_path)
    with status_lock:
        statuses.append(res['status'])
threads = [threading.Thread(target=_call) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
assert call_count['n'] == 1, f"migrate() ran {call_count['n']}x instead of exactly once"
assert statuses.count('applied') == 1
for s in statuses:
    assert s in ('applied', 'already_applied', 'deferred'), s
```

## Next Steps


---

*Source: test_migration_daemon_safety.py:90 | Complexity: Advanced | Last updated: 2026-05-05*