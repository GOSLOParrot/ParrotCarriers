# How To: Tools With Graph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Tools with a pre-populated graph.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `asyncio`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.models`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `superlocalmemory.code_graph.config`
- `superlocalmemory.code_graph.service`
- `superlocalmemory.mcp`

**Setup Required:**
```python
# Fixtures: db, tools
```

## Step-by-Step Guide

### Step 1: 'Tools with a pre-populated graph.'

```python
'Tools with a pre-populated graph.'
```

### Step 2: Assign ids = _insert_test_graph(...)

```python
ids = _insert_test_graph(db)
```

### Step 3: Assign config = CodeGraphConfig(...)

```python
config = CodeGraphConfig(enabled=True, db_path=db.db_path)
```

### Step 4: Assign svc = CodeGraphService(...)

```python
svc = CodeGraphService(config)
```

### Step 5: Assign svc._db = db

```python
svc._db = db
```

### Step 6: Assign tools_code_graph._service = svc

```python
tools_code_graph._service = svc
```


## Complete Example

```python
# Setup
# Fixtures: db, tools

# Workflow
'Tools with a pre-populated graph.'
from superlocalmemory.mcp import tools_code_graph
from superlocalmemory.code_graph.config import CodeGraphConfig
from superlocalmemory.code_graph.service import CodeGraphService
ids = _insert_test_graph(db)
config = CodeGraphConfig(enabled=True, db_path=db.db_path)
svc = CodeGraphService(config)
svc._db = db
tools_code_graph._service = svc
return (tools, ids)
```

## Next Steps


---

*Source: test_mcp_tools.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*