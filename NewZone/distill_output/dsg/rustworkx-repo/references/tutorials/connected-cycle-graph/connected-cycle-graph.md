# How To: Connected Cycle Graph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test connected cycle graph

## Prerequisites

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_cycle_graph(...)

```python
graph = rustworkx.generators.directed_cycle_graph(32)
```

### Step 2: Assign res = rustworkx.unweighted_average_shortest_path_length(...)

```python
res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
```

### Step 3: Assign s = 8192

```python
s = 8192
```

### Step 4: Assign den = 992

```python
den = 992
```

### Step 5: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(s / den, res, delta=1e-07)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
s = 8192
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

## Next Steps


---

*Source: test_avg_shortest_path.py:164 | Complexity: Intermediate | Last updated: 2026-05-05*