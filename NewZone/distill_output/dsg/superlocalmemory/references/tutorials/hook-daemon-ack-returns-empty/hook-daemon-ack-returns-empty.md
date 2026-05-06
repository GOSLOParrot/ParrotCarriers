# How To: Hook Daemon Ack Returns Empty

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Ack prompts through socket return empty dict.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `socket`
- `tempfile`
- `time`
- `pathlib`
- `unittest.mock`
- `pytest`
- `shutil`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `superlocalmemory.hooks.hook_daemon`
- `importlib`
- `sys`

**Setup Required:**
```python
# Fixtures: short_tmp
```

## Step-by-Step Guide

### Step 1: 'Ack prompts through socket return empty dict.'

```python
'Ack prompts through socket return empty dict.'
```

**Verification:**
```python
assert response == {}
```

### Step 2: Assign sock_path = value

```python
sock_path = short_tmp / 'hook.sock'
```

### Step 3: Assign daemon = HookDaemon(...)

```python
daemon = HookDaemon(sock_path=sock_path, queue_db_path=short_tmp / 'q.db')
```

### Step 4: Call daemon.start()

```python
daemon.start()
```

### Step 5: Call time.sleep()

```python
time.sleep(0.1)
```

### Step 6: Assign client = socket.socket(...)

```python
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
```

### Step 7: Call client.settimeout()

```python
client.settimeout(5.0)
```

### Step 8: Call client.connect()

```python
client.connect(str(sock_path))
```

### Step 9: Assign request = value

```python
request = json.dumps({'prompt': 'yes', 'session_id': 'test'}) + '\n'
```

### Step 10: Call client.sendall()

```python
client.sendall(request.encode('utf-8'))
```

### Step 11: Assign data = b''

```python
data = b''
```

### Step 12: Assign response = json.loads(...)

```python
response = json.loads(data.decode('utf-8').strip())
```

**Verification:**
```python
assert response == {}
```

### Step 13: Call client.close()

```python
client.close()
```

### Step 14: Call daemon.stop()

```python
daemon.stop()
```

### Step 15: Assign chunk = client.recv(...)

```python
chunk = client.recv(4096)
```


## Complete Example

```python
# Setup
# Fixtures: short_tmp

# Workflow
'Ack prompts through socket return empty dict.'
from superlocalmemory.hooks.hook_daemon import HookDaemon
sock_path = short_tmp / 'hook.sock'
daemon = HookDaemon(sock_path=sock_path, queue_db_path=short_tmp / 'q.db')
daemon.start()
time.sleep(0.1)
try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(5.0)
    client.connect(str(sock_path))
    request = json.dumps({'prompt': 'yes', 'session_id': 'test'}) + '\n'
    client.sendall(request.encode('utf-8'))
    data = b''
    while b'\n' not in data:
        chunk = client.recv(4096)
        if not chunk:
            break
        data += chunk
    response = json.loads(data.decode('utf-8').strip())
    assert response == {}
    client.close()
finally:
    daemon.stop()
```

## Next Steps


---

*Source: test_hook_daemon.py:118 | Complexity: Advanced | Last updated: 2026-05-05*