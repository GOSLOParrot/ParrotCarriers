# How To: Python Copy Check Cycle

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test python copy check cycle

## Prerequisites

**Required Modules:**
- `unittest`
- `copy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_a = rustworkx.PyDiGraph(...)

```python
graph_a = rustworkx.PyDiGraph(check_cycle=True)
```

### Step 2: Assign graph_b = copy.copy(...)

```python
graph_b = copy.copy(graph_a)
```

### Step 3: Assign graph_c = rustworkx.PyDiGraph(...)

```python
graph_c = rustworkx.PyDiGraph(check_cycle=False)
```

### Step 4: Assign graph_d = copy.copy(...)

```python
graph_d = copy.copy(graph_c)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(graph_b.check_cycle)
```

### Step 6: Call self.assertFalse()

```python
self.assertFalse(graph_d.check_cycle)
```


## Complete Example

```python
# Workflow
graph_a = rustworkx.PyDiGraph(check_cycle=True)
graph_b = copy.copy(graph_a)
graph_c = rustworkx.PyDiGraph(check_cycle=False)
graph_d = copy.copy(graph_c)
self.assertTrue(graph_b.check_cycle)
self.assertFalse(graph_d.check_cycle)
```

## Next Steps


---

*Source: test_copy.py:58 | Complexity: Intermediate | Last updated: 2026-05-05*