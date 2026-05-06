# How To: Hexagonal Graph Periodic Subgraphs

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Check that hexagonal subgraphs of the lattice are isomorphic
to C6 (idea copied from the networkx test suite).

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`
- `numpy`
- `rustworkx.generators`


## Step-by-Step Guide

### Step 1: 'Check that hexagonal subgraphs of the lattice are isomorphic\n        to C6 (idea copied from the networkx test suite).'

```python
'Check that hexagonal subgraphs of the lattice are isomorphic\n        to C6 (idea copied from the networkx test suite).'
```

### Step 2: Assign graph = rustworkx.generators.hexagonal_lattice_graph(...)

```python
graph = rustworkx.generators.hexagonal_lattice_graph(2, 4, periodic=True)
```

### Step 3: Assign hexagons = value

```python
hexagons = [[0, 1, 2, 6, 5, 4], [2, 3, 0, 4, 7, 6], [5, 6, 7, 11, 10, 9]]
```

### Step 4: Assign C6 = rustworkx.generators.cycle_graph(...)

```python
C6 = rustworkx.generators.cycle_graph(6)
```

### Step 5: Assign graph2cols = rustworkx.generators.hexagonal_lattice_graph(...)

```python
graph2cols = rustworkx.generators.hexagonal_lattice_graph(2, 2, periodic=True)
```

### Step 6: Assign subGraph = graph2cols.subgraph(...)

```python
subGraph = graph2cols.subgraph(hexagons[0])
```

### Step 7: Call self.assertFalse()

```python
self.assertFalse(rustworkx.is_isomorphic(subGraph, C6))
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(len(subGraph.edges()), 7)
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
```


## Complete Example

```python
# Workflow
'Check that hexagonal subgraphs of the lattice are isomorphic\n        to C6 (idea copied from the networkx test suite).'
graph = rustworkx.generators.hexagonal_lattice_graph(2, 4, periodic=True)
hexagons = [[0, 1, 2, 6, 5, 4], [2, 3, 0, 4, 7, 6], [5, 6, 7, 11, 10, 9]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
graph2cols = rustworkx.generators.hexagonal_lattice_graph(2, 2, periodic=True)
subGraph = graph2cols.subgraph(hexagons[0])
self.assertFalse(rustworkx.is_isomorphic(subGraph, C6))
self.assertEqual(len(subGraph.edges()), 7)
```

## Next Steps


---

*Source: test_hexagonal.py:423 | Complexity: Advanced | Last updated: 2026-05-05*