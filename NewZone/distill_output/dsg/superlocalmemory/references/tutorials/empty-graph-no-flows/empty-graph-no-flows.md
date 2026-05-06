# How To: Empty Graph No Flows

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Empty graph returns no flows.

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
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: 'Empty graph returns no flows.'

```python
'Empty graph returns no flows.'
```

**Verification:**
```python
assert detector.trace_all_flows() == []
```

### Step 2: Assign detector = FlowDetector(...)

```python
detector = FlowDetector(db)
```

**Verification:**
```python
assert detector.trace_all_flows() == []
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
'Empty graph returns no flows.'
detector = FlowDetector(db)
assert detector.trace_all_flows() == []
```

## Next Steps


---

*Source: test_flows.py:284 | Complexity: Beginner | Last updated: 2026-05-05*