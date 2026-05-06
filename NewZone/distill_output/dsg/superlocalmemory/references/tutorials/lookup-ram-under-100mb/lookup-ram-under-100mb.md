# How To: Lookup Ram Under 100Mb

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Steady-state RAM delta from the lookup LRU + open connection
must stay under 100 MB. Per LLD-13 §10.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`
- `contextlib`
- `superlocalmemory.learning`
- `contextlib`
- `psutil`
- `os`
- `superlocalmemory.learning`
- `sqlite3`
- `superlocalmemory.learning.trigram_index`
- `inspect`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: index
```

## Step-by-Step Guide

### Step 1: 'Steady-state RAM delta from the lookup LRU + open connection\n    must stay under 100 MB. Per LLD-13 §10.'

```python
'Steady-state RAM delta from the lookup LRU + open connection\n    must stay under 100 MB. Per LLD-13 §10.'
```

**Verification:**
```python
assert delta_mb < 100, f'lookup RSS delta {delta_mb:.1f} MB exceeds 100 MB'
```

### Step 2: Call index.bootstrap()

```python
index.bootstrap()
```

### Step 3: Assign proc = psutil.Process(...)

```python
proc = psutil.Process(os.getpid())
```

### Step 4: Assign rss_before = value

```python
rss_before = proc.memory_info().rss
```

### Step 5: Assign rss_after = value

```python
rss_after = proc.memory_info().rss
```

### Step 6: Assign delta_mb = value

```python
delta_mb = (rss_after - rss_before) / (1024 * 1024)
```

**Verification:**
```python
assert delta_mb < 100, f'lookup RSS delta {delta_mb:.1f} MB exceeds 100 MB'
```

### Step 7: Call index.lookup()

```python
index.lookup(f'prompt {i} SuperLocalMemory Qualixar AgentAssert')
```


## Complete Example

```python
# Setup
# Fixtures: index

# Workflow
'Steady-state RAM delta from the lookup LRU + open connection\n    must stay under 100 MB. Per LLD-13 §10.'
import psutil, os
index.bootstrap()
proc = psutil.Process(os.getpid())
rss_before = proc.memory_info().rss
for i in range(5000):
    index.lookup(f'prompt {i} SuperLocalMemory Qualixar AgentAssert')
rss_after = proc.memory_info().rss
delta_mb = (rss_after - rss_before) / (1024 * 1024)
assert delta_mb < 100, f'lookup RSS delta {delta_mb:.1f} MB exceeds 100 MB'
```

## Next Steps


---

*Source: test_trigram_index.py:244 | Complexity: Intermediate | Last updated: 2026-05-05*