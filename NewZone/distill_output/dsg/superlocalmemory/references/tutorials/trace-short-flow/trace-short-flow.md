# How To: Trace Short Flow

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Handle event -> process event is a 2-node flow.

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

### Step 1: 'Handle event -> process event is a 2-node flow.'

```python
'Handle event -> process event is a 2-node flow.'
```

**Verification:**
```python
assert flow.node_count == 2
```

### Step 2: Assign flow = detector.trace_flow(...)

```python
flow = detector.trace_flow('handle_event')
```

**Verification:**
```python
assert 'handle_event' in flow.path_node_ids
```


## Complete Example

```python
# Setup
# Fixtures: detector

# Workflow
'Handle event -> process event is a 2-node flow.'
flow = detector.trace_flow('handle_event')
assert flow.node_count == 2
assert 'handle_event' in flow.path_node_ids
assert 'process_event' in flow.path_node_ids
```

## Next Steps


---

*Source: test_flows.py:202 | Complexity: Beginner | Last updated: 2026-05-05*