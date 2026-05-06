# How To: Hexagonal Graph With Positions

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test hexagonal graph with positions

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`
- `numpy`
- `rustworkx.generators`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.hexagonal_lattice_graph(...)

```python
graph = rustworkx.generators.hexagonal_lattice_graph(2, 2, with_positions=True)
```

### Step 2: Assign positions = graph.nodes(...)

```python
positions = graph.nodes()
```

### Step 3: Assign hexagons = value

```python
hexagons = [[0, 1, 2, 7, 6, 5], [2, 3, 4, 9, 8, 7], [6, 7, 8, 13, 12, 11], [8, 9, 10, 15, 14, 13]]
```

### Step 4: Assign C6 = rustworkx.generators.cycle_graph(...)

```python
C6 = rustworkx.generators.cycle_graph(6)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
```

### Step 6: Assign coordinates = np.array(...)

```python
coordinates = np.array([positions[node] for node in h])
```

### Step 7: Assign vectors = value

```python
vectors = [coordinates[(ii + 1) % 6] - coordinates[ii] for ii in range(6)]
```

### Step 8: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(np.linalg.norm(v), 1.0, 12)
```

### Step 9: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(np.dot(vectors[ii], vectors[(ii + 1) % 6]), np.cos(np.pi / 3), 12)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.hexagonal_lattice_graph(2, 2, with_positions=True)
positions = graph.nodes()
hexagons = [[0, 1, 2, 7, 6, 5], [2, 3, 4, 9, 8, 7], [6, 7, 8, 13, 12, 11], [8, 9, 10, 15, 14, 13]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
    coordinates = np.array([positions[node] for node in h])
    vectors = [coordinates[(ii + 1) % 6] - coordinates[ii] for ii in range(6)]
    for v in vectors:
        self.assertAlmostEqual(np.linalg.norm(v), 1.0, 12)
    for ii in range(6):
        self.assertAlmostEqual(np.dot(vectors[ii], vectors[(ii + 1) % 6]), np.cos(np.pi / 3), 12)
```

## Next Steps


---

*Source: test_hexagonal.py:588 | Complexity: Advanced | Last updated: 2026-05-05*