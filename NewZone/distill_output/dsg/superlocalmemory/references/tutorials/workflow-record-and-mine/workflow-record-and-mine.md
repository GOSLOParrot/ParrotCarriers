# How To: Workflow Record And Mine

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test workflow record and mine

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `superlocalmemory.learning.bootstrap`
- `superlocalmemory.learning.workflows`
- `superlocalmemory.learning.cross_project`
- `superlocalmemory.learning.project_context`

**Setup Required:**
```python
# Fixtures: workflow
```

## Step-by-Step Guide

### Step 1: Call workflow.record_action()

```python
workflow.record_action('p1', 'store', {'topic': 'auth'})
```

**Verification:**
```python
assert isinstance(patterns, list)
```

### Step 2: Call workflow.record_action()

```python
workflow.record_action('p1', 'recall', {'topic': 'auth'})
```

### Step 3: Call workflow.record_action()

```python
workflow.record_action('p1', 'store', {'topic': 'auth'})
```

### Step 4: Assign patterns = workflow.mine(...)

```python
patterns = workflow.mine('p1')
```

**Verification:**
```python
assert isinstance(patterns, list)
```


## Complete Example

```python
# Setup
# Fixtures: workflow

# Workflow
workflow.record_action('p1', 'store', {'topic': 'auth'})
workflow.record_action('p1', 'recall', {'topic': 'auth'})
workflow.record_action('p1', 'store', {'topic': 'auth'})
patterns = workflow.mine('p1')
assert isinstance(patterns, list)
```

## Next Steps


---

*Source: test_learning_advanced.py:47 | Complexity: Intermediate | Last updated: 2026-05-05*