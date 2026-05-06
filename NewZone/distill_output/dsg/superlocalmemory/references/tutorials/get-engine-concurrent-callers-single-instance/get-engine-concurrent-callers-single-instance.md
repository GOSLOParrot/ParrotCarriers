# How To: Get Engine Concurrent Callers Single Instance

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: FastMCP dispatches tools from multiple threads. Two threads
racing on a cold ``get_engine()`` must see the same instance and
must only construct the engine once.

## Prerequisites

**Required Modules:**
- `__future__`
- `os`
- `subprocess`
- `sys`
- `pytest`
- `superlocalmemory.core.engine_capabilities`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `threading`
- `superlocalmemory.mcp`
- `superlocalmemory.core.engine`


## Step-by-Step Guide

### Step 1: 'FastMCP dispatches tools from multiple threads. Two threads\n    racing on a cold ``get_engine()`` must see the same instance and\n    must only construct the engine once.'

```python
'FastMCP dispatches tools from multiple threads. Two threads\n    racing on a cold ``get_engine()`` must see the same instance and\n    must only construct the engine once.'
```

**Verification:**
```python
assert construct_counter['n'] == 1, f"get_engine double-constructed: {construct_counter['n']}x"
```

### Step 2: Call server.reset_engine()

```python
server.reset_engine()
```

**Verification:**
```python
assert all((e is first for e in engines)), 'threads saw different engine instances'
```

### Step 3: Assign construct_counter = value

```python
construct_counter = {'n': 0}
```

### Step 4: Assign original_init = None

```python
original_init = None
```

### Step 5: Assign original_init = value

```python
original_init = MemoryEngine.__init__
```

### Step 6: Assign MemoryEngine.__init__ = _counting_init

```python
MemoryEngine.__init__ = _counting_init
```

### Step 7: Assign threads = value

```python
threads = [threading.Thread(target=_call) for _ in range(16)]
```

**Verification:**
```python
assert construct_counter['n'] == 1, f"get_engine double-constructed: {construct_counter['n']}x"
```

### Step 8: Assign first = value

```python
first = engines[0]
```

**Verification:**
```python
assert all((e is first for e in engines)), 'threads saw different engine instances'
```

### Step 9: Assign MemoryEngine.__init__ = original_init

```python
MemoryEngine.__init__ = original_init
```

### Step 10: Call server.reset_engine()

```python
server.reset_engine()
```

### Step 11: Call engines.append()

```python
engines.append(server.get_engine())
```

### Step 12: Call t.start()

```python
t.start()
```

### Step 13: Call t.join()

```python
t.join()
```


## Complete Example

```python
# Workflow
'FastMCP dispatches tools from multiple threads. Two threads\n    racing on a cold ``get_engine()`` must see the same instance and\n    must only construct the engine once.'
import threading
from superlocalmemory.mcp import server
server.reset_engine()
construct_counter = {'n': 0}
original_init = None

def _counting_init(self, config, **kw):
    construct_counter['n'] += 1
    return original_init(self, config, **kw)
from superlocalmemory.core.engine import MemoryEngine
original_init = MemoryEngine.__init__
try:
    MemoryEngine.__init__ = _counting_init
    engines: list = []

    def _call():
        engines.append(server.get_engine())
    threads = [threading.Thread(target=_call) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert construct_counter['n'] == 1, f"get_engine double-constructed: {construct_counter['n']}x"
    first = engines[0]
    assert all((e is first for e in engines)), 'threads saw different engine instances'
finally:
    MemoryEngine.__init__ = original_init
    server.reset_engine()
```

## Next Steps


---

*Source: test_mcp_light_engine.py:53 | Complexity: Advanced | Last updated: 2026-05-05*