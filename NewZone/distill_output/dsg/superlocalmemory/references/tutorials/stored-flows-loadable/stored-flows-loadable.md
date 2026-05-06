# How To: Stored Flows Loadable

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Stored flows can be loaded back.

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
# Fixtures: detector
```

## Step-by-Step Guide

### Step 1: 'Stored flows can be loaded back.'

```python
'Stored flows can be loaded back.'
```

**Verification:**
```python
assert len(loaded) == len(original)
```

### Step 2: Assign original = detector.trace_all_flows(...)

```python
original = detector.trace_all_flows()
```

**Verification:**
```python
assert orig.name == load.name
```

### Step 3: Assign loaded = detector.get_stored_flows(...)

```python
loaded = detector.get_stored_flows()
```

**Verification:**
```python
assert orig.entry_node_id == load.entry_node_id
```


## Complete Example

```python
# Setup
# Fixtures: detector

# Workflow
'Stored flows can be loaded back.'
original = detector.trace_all_flows()
loaded = detector.get_stored_flows()
assert len(loaded) == len(original)
for orig, load in zip(original, loaded):
    assert orig.name == load.name
    assert orig.entry_node_id == load.entry_node_id
```

## Next Steps


---

*Source: test_flows.py:275 | Complexity: Beginner | Last updated: 2026-05-05*