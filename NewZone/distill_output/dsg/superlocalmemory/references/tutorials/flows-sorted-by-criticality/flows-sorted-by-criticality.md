# How To: Flows Sorted By Criticality

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Flows are sorted by criticality descending.

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

### Step 1: 'Flows are sorted by criticality descending.'

```python
'Flows are sorted by criticality descending.'
```

**Verification:**
```python
assert flows[i].criticality >= flows[i + 1].criticality
```

### Step 2: Assign flows = detector.trace_all_flows(...)

```python
flows = detector.trace_all_flows()
```

**Verification:**
```python
assert flows[i].criticality >= flows[i + 1].criticality
```


## Complete Example

```python
# Setup
# Fixtures: detector

# Workflow
'Flows are sorted by criticality descending.'
flows = detector.trace_all_flows()
if len(flows) >= 2:
    for i in range(len(flows) - 1):
        assert flows[i].criticality >= flows[i + 1].criticality
```

## Next Steps


---

*Source: test_flows.py:258 | Complexity: Beginner | Last updated: 2026-05-05*