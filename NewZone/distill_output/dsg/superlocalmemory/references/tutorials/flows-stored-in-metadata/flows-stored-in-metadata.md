# How To: Flows Stored In Metadata

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Flows are stored in graph_metadata.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `time`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.flows`
- `superlocalmemory.code_graph.models`

**Setup Required:**
```python
# Fixtures: detector, flow_db
```

## Step-by-Step Guide

### Step 1: 'Flows are stored in graph_metadata.'

```python
'Flows are stored in graph_metadata.'
```

**Verification:**
```python
assert raw is not None
```

### Step 2: Call detector.trace_all_flows()

```python
detector.trace_all_flows()
```

**Verification:**
```python
assert len(data) >= 2
```

### Step 3: Assign raw = flow_db.get_metadata(...)

```python
raw = flow_db.get_metadata('flows')
```

**Verification:**
```python
assert raw is not None
```

### Step 4: Assign data = json.loads(...)

```python
data = json.loads(raw)
```

**Verification:**
```python
assert len(data) >= 2
```


## Complete Example

```python
# Setup
# Fixtures: detector, flow_db

# Workflow
'Flows are stored in graph_metadata.'
detector.trace_all_flows()
raw = flow_db.get_metadata('flows')
assert raw is not None
data = json.loads(raw)
assert len(data) >= 2
```

## Next Steps


---

*Source: test_flows.py:265 | Complexity: Intermediate | Last updated: 2026-05-05*