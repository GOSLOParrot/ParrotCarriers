# How To: Rate Limit Resets After Hour

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rate limit resets after hour

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `os`
- `sqlite3`
- `tempfile`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.ingestion.parsers`
- `superlocalmemory.ingestion.parsers`
- `superlocalmemory.ingestion.parsers`
- `superlocalmemory.ingestion.parsers`
- `superlocalmemory.ingestion.parsers`
- `superlocalmemory.ingestion.base_adapter`
- `time`
- `superlocalmemory.ingestion.base_adapter`
- `superlocalmemory.ingestion.base_adapter`
- `superlocalmemory.ingestion.adapter_manager`
- `superlocalmemory.ingestion.adapter_manager`
- `superlocalmemory.ingestion.adapter_manager`
- `superlocalmemory.ingestion.credentials`
- `superlocalmemory.ingestion.credentials`
- `superlocalmemory.ingestion.adapter_manager`
- `importlib`
- `superlocalmemory.ingestion.credentials`


## Step-by-Step Guide

### Step 1: Assign config = AdapterConfig(...)

```python
config = AdapterConfig(rate_limit_per_hour=3)
```

**Verification:**
```python
assert adapter._rate_limited() is False
```

### Step 2: Assign adapter = BaseAdapter(...)

```python
adapter = BaseAdapter(config)
```

### Step 3: Assign adapter._items_this_hour = 3

```python
adapter._items_this_hour = 3
```

### Step 4: Assign adapter._hour_start = value

```python
adapter._hour_start = time.time() - 3601
```

**Verification:**
```python
assert adapter._rate_limited() is False
```


## Complete Example

```python
# Workflow
import time
from superlocalmemory.ingestion.base_adapter import BaseAdapter, AdapterConfig
config = AdapterConfig(rate_limit_per_hour=3)
adapter = BaseAdapter(config)
adapter._items_this_hour = 3
adapter._hour_start = time.time() - 3601
assert adapter._rate_limited() is False
```

## Next Steps


---

*Source: test_ingestion.py:102 | Complexity: Intermediate | Last updated: 2026-05-05*