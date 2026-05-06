# How To: Condensation With Sccs Argument

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test condensation with sccs argument

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign sccs = rustworkx.strongly_connected_components(...)

```python
sccs = rustworkx.strongly_connected_components(self.graph)
```

### Step 2: Assign condensed_graph = rustworkx.condensation(...)

```python
condensed_graph = rustworkx.condensation(self.graph, sccs=sccs)
```

### Step 3: condensed_graph.attrs['node_map']

```python
condensed_graph.attrs['node_map']
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(len(condensed_graph.node_indices()), len(sccs))
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(condensed_graph.edge_indices()), 1)
```

### Step 6: Assign nodes = list(...)

```python
nodes = list(condensed_graph.nodes())
```

### Step 7: Assign scc_sets = value

```python
scc_sets = [set(n) for n in nodes]
```

### Step 8: Call self.assertIn()

```python
self.assertIn(set(['a', 'b', 'c', 'd']), scc_sets)
```

### Step 9: Call self.assertIn()

```python
self.assertIn(set(['e', 'f', 'g', 'h']), scc_sets)
```

### Step 10: Assign weight = value

```python
weight = condensed_graph.edges()[0]
```

### Step 11: Call self.assertIn()

```python
self.assertIn('b->e', weight)
```


## Complete Example

```python
# Workflow
sccs = rustworkx.strongly_connected_components(self.graph)
condensed_graph = rustworkx.condensation(self.graph, sccs=sccs)
condensed_graph.attrs['node_map']
self.assertEqual(len(condensed_graph.node_indices()), len(sccs))
self.assertEqual(len(condensed_graph.edge_indices()), 1)
nodes = list(condensed_graph.nodes())
scc_sets = [set(n) for n in nodes]
self.assertIn(set(['a', 'b', 'c', 'd']), scc_sets)
self.assertIn(set(['e', 'f', 'g', 'h']), scc_sets)
weight = condensed_graph.edges()[0]
self.assertIn('b->e', weight)
```

## Next Steps


---

*Source: test_strongly_connected.py:156 | Complexity: Advanced | Last updated: 2026-05-05*