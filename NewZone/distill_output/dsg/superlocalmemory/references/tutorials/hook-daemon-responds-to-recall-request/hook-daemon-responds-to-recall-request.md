# How To: Hook Daemon Responds To Recall Request

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Client sends recall request via socket, gets response (even empty).

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

### Step 1: 'Client sends recall request via socket, gets response (even empty).'

```python
'Client sends recall request via socket, gets response (even empty).'
```

**Verification:**
```python
assert isinstance(response, dict)
```

### Step 2: Assign sock_path = value

```python
sock_path = short_tmp / 'hook.sock'
```

### Step 3: Assign queue_db = value

```python
queue_db = short_tmp / 'q.db'
```

### Step 4: Assign daemon = HookDaemon(...)

```python
daemon = HookDaemon(sock_path=sock_path, queue_db_path=queue_db)
```

### Step 5: Call daemon.start()

```python
daemon.start()
```

### Step 6: Call time.sleep()

```python
time.sleep(0.1)
```

### Step 7: Call daemon.stop()

```python
daemon.stop()
```

### Step 8: Assign client = socket.socket(...)

```python
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
```

### Step 9: Call client.settimeout()

```python
client.settimeout(5.0)
```

### Step 10: Call client.connect()

```python
client.connect(str(sock_path))
```

### Step 11: Assign request = value

```python
request = json.dumps({'prompt': 'What is the recall queue?', 'session_id': 'test-sock'}) + '\n'
```

### Step 12: Call client.sendall()

```python
client.sendall(request.encode('utf-8'))
```

### Step 13: Assign data = b''

```python
data = b''
```

### Step 14: Assign response = json.loads(...)

```python
response = json.loads(data.decode('utf-8').strip())
```

**Verification:**
```python
assert isinstance(response, dict)
```

### Step 15: Call client.close()

```python
client.close()
```

### Step 16: Assign chunk = client.recv(...)

```python
chunk = client.recv(4096)
```


## Complete Example

```python
# Setup
# Fixtures: short_tmp

# Workflow
'Client sends recall request via socket, gets response (even empty).'
from superlocalmemory.hooks.hook_daemon import HookDaemon
sock_path = short_tmp / 'hook.sock'
queue_db = short_tmp / 'q.db'
daemon = HookDaemon(sock_path=sock_path, queue_db_path=queue_db)
daemon.start()
time.sleep(0.1)
try:
    with patch('superlocalmemory.hooks.auto_recall_hook._get_mode_timeout', return_value=1.0), patch('superlocalmemory.hooks.auto_recall_hook._detect_mode', return_value='A'):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(5.0)
        client.connect(str(sock_path))
        request = json.dumps({'prompt': 'What is the recall queue?', 'session_id': 'test-sock'}) + '\n'
        client.sendall(request.encode('utf-8'))
        data = b''
        while b'\n' not in data:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk
        response = json.loads(data.decode('utf-8').strip())
        assert isinstance(response, dict)
        client.close()
finally:
    daemon.stop()
```

## Next Steps


---

*Source: test_hook_daemon.py:79 | Complexity: Advanced | Last updated: 2026-05-05*