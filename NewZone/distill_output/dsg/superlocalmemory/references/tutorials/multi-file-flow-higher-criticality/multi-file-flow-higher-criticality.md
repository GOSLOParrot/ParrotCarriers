# How To: Multi File Flow Higher Criticality

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Flows spanning multiple files score higher on file_spread.

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

### Step 1: 'Flows spanning multiple files score higher on file_spread.'

```python
'Flows spanning multiple files score higher on file_spread.'
```

**Verification:**
```python
assert main_flows[0].file_count >= event_flows[0].file_count
```

### Step 2: Assign flows = detector.trace_all_flows(...)

```python
flows = detector.trace_all_flows()
```

### Step 3: Assign main_flows = value

```python
main_flows = [f for f in flows if f.name == 'flow_main']
```

### Step 4: Assign event_flows = value

```python
event_flows = [f for f in flows if f.name == 'flow_handle_event']
```

**Verification:**
```python
assert main_flows[0].file_count >= event_flows[0].file_count
```


## Complete Example

```python
# Setup
# Fixtures: detector

# Workflow
'Flows spanning multiple files score higher on file_spread.'
flows = detector.trace_all_flows()
if len(flows) >= 2:
    main_flows = [f for f in flows if f.name == 'flow_main']
    event_flows = [f for f in flows if f.name == 'flow_handle_event']
    if main_flows and event_flows:
        assert main_flows[0].file_count >= event_flows[0].file_count
```

## Next Steps


---

*Source: test_flows.py:223 | Complexity: Intermediate | Last updated: 2026-05-05*