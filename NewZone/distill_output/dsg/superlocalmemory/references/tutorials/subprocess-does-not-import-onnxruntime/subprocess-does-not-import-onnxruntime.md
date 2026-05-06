# How To: Subprocess Does Not Import Onnxruntime

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Spawn a fresh subprocess that imports mcp.server and calls
get_engine(). Assert onnxruntime is NOT in sys.modules after init.

This is the load-bearing contract: LIGHT means the ONNX embedder
module never loads, which is what keeps multi-IDE RSS bounded.

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

### Step 1: 'Spawn a fresh subprocess that imports mcp.server and calls\n    get_engine(). Assert onnxruntime is NOT in sys.modules after init.\n\n    This is the load-bearing contract: LIGHT means the ONNX embedder\n    module never loads, which is what keeps multi-IDE RSS bounded.\n    '

```python
'Spawn a fresh subprocess that imports mcp.server and calls\n    get_engine(). Assert onnxruntime is NOT in sys.modules after init.\n\n    This is the load-bearing contract: LIGHT means the ONNX embedder\n    module never loads, which is what keeps multi-IDE RSS bounded.\n    '
```

**Verification:**
```python
assert 'ONNX_LOADED=False' in out, f'ONNX was loaded into MCP process: {out}'
```

### Step 2: Assign script = "import os; os.environ['SLM_DISABLE_WARMUP_SIDE_EFFECTS'] = '1'; from superlocalmemory.mcp import server; engine = server.get_engine(); import sys; loaded = any(m.startswith('onnxruntime') for m in sys.modules); embedder_none = engine._embedder is None; caps = engine.capabilities.value; print(f'ONNX_LOADED={loaded};EMBEDDER_NONE={embedder_none};CAPS={caps}')"

```python
script = "import os; os.environ['SLM_DISABLE_WARMUP_SIDE_EFFECTS'] = '1'; from superlocalmemory.mcp import server; engine = server.get_engine(); import sys; loaded = any(m.startswith('onnxruntime') for m in sys.modules); embedder_none = engine._embedder is None; caps = engine.capabilities.value; print(f'ONNX_LOADED={loaded};EMBEDDER_NONE={embedder_none};CAPS={caps}')"
```

**Verification:**
```python
assert 'EMBEDDER_NONE=True' in out, f'Embedder leaked: {out}'
```

### Step 3: Assign proc = subprocess.run(...)

```python
proc = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=60, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
```

**Verification:**
```python
assert 'CAPS=light' in out, f'Engine not LIGHT: {out}'
```

### Step 4: Assign out = value

```python
out = proc.stdout.strip().splitlines()[-1]
```

**Verification:**
```python
assert 'ONNX_LOADED=False' in out, f'ONNX was loaded into MCP process: {out}'
```

### Step 5: Call pytest.fail()

```python
pytest.fail(f'subprocess failed:\nstdout:{proc.stdout}\nstderr:{proc.stderr}')
```


## Complete Example

```python
# Workflow
'Spawn a fresh subprocess that imports mcp.server and calls\n    get_engine(). Assert onnxruntime is NOT in sys.modules after init.\n\n    This is the load-bearing contract: LIGHT means the ONNX embedder\n    module never loads, which is what keeps multi-IDE RSS bounded.\n    '
script = "import os; os.environ['SLM_DISABLE_WARMUP_SIDE_EFFECTS'] = '1'; from superlocalmemory.mcp import server; engine = server.get_engine(); import sys; loaded = any(m.startswith('onnxruntime') for m in sys.modules); embedder_none = engine._embedder is None; caps = engine.capabilities.value; print(f'ONNX_LOADED={loaded};EMBEDDER_NONE={embedder_none};CAPS={caps}')"
proc = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=60, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
if proc.returncode != 0:
    pytest.fail(f'subprocess failed:\nstdout:{proc.stdout}\nstderr:{proc.stderr}')
out = proc.stdout.strip().splitlines()[-1]
assert 'ONNX_LOADED=False' in out, f'ONNX was loaded into MCP process: {out}'
assert 'EMBEDDER_NONE=True' in out, f'Embedder leaked: {out}'
assert 'CAPS=light' in out, f'Engine not LIGHT: {out}'
```

## Next Steps


---

*Source: test_mcp_light_engine.py:93 | Complexity: Intermediate | Last updated: 2026-05-05*