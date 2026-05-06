# How To: Digraph Vf2 Number Of Valid Mappings

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test digraph vf2 number of valid mappings

## Prerequisites

**Required Modules:**
- `copy`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_mesh_graph(...)

```python
graph = rustworkx.generators.directed_mesh_graph(3)
```

### Step 2: Assign mapping = rustworkx.digraph_vf2_mapping(...)

```python
mapping = rustworkx.digraph_vf2_mapping(graph, graph, id_order=True)
```

### Step 3: Assign total = 0

```python
total = 0
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(total, 6)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_mesh_graph(3)
mapping = rustworkx.digraph_vf2_mapping(graph, graph, id_order=True)
total = 0
for _ in mapping:
    total += 1
self.assertEqual(total, 6)
```

## Next Steps


---

*Source: test_isomorphic.py:336 | Complexity: Intermediate | Last updated: 2026-05-05*