# How To: Finds Multiple Flows

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Detects flows from all entry points.

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

### Step 1: 'Detects flows from all entry points.'

```python
'Detects flows from all entry points.'
```

**Verification:**
```python
assert len(flows) >= 2
```

### Step 2: Assign flows = detector.trace_all_flows(...)

```python
flows = detector.trace_all_flows()
```

**Verification:**
```python
assert len(flows) >= 2
```


## Complete Example

```python
# Setup
# Fixtures: detector

# Workflow
'Detects flows from all entry points.'
flows = detector.trace_all_flows()
assert len(flows) >= 2
```

## Next Steps


---

*Source: test_flows.py:253 | Complexity: Beginner | Last updated: 2026-05-05*