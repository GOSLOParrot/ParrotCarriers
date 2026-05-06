# How To: Trace Main Flow

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Tracing from main follows CALLS edges.

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

### Step 1: 'Tracing from main follows CALLS edges.'

```python
'Tracing from main follows CALLS edges.'
```

**Verification:**
```python
assert isinstance(flow, FlowResult)
```

### Step 2: Assign flow = detector.trace_flow(...)

```python
flow = detector.trace_flow('main')
```

**Verification:**
```python
assert flow.entry_node_id == 'main'
```


## Complete Example

```python
# Setup
# Fixtures: detector

# Workflow
'Tracing from main follows CALLS edges.'
flow = detector.trace_flow('main')
assert isinstance(flow, FlowResult)
assert flow.entry_node_id == 'main'
assert flow.node_count >= 2
assert 'main' in flow.path_node_ids
assert 'process_request' in flow.path_node_ids
```

## Next Steps


---

*Source: test_flows.py:170 | Complexity: Beginner | Last updated: 2026-05-05*