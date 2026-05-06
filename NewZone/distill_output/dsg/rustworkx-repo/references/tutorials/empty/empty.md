# How To: Empty

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test empty

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign N = 5

```python
N = 5
```

### Step 2: Assign graph = rustworkx.generators.empty_graph(...)

```python
graph = rustworkx.generators.empty_graph(N, multigraph=False)
```

### Step 3: Assign expected_graph = rustworkx.generators.empty_graph(...)

```python
expected_graph = rustworkx.generators.empty_graph(N, multigraph=False)
```

### Step 4: Assign complement_graph = rustworkx.local_complement(...)

```python
complement_graph = rustworkx.local_complement(graph, 0)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```


## Complete Example

```python
# Workflow
N = 5
graph = rustworkx.generators.empty_graph(N, multigraph=False)
expected_graph = rustworkx.generators.empty_graph(N, multigraph=False)
complement_graph = rustworkx.local_complement(graph, 0)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

## Next Steps


---

*Source: test_local_complement.py:48 | Complexity: Intermediate | Last updated: 2026-05-05*