# How To: Topo Sort Progress If Graph Has Cycle And Cycle Check Disabled

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test topo sort progress if graph has cycle and cycle check disabled

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_cycle_graph(...)

```python
graph = rustworkx.generators.directed_cycle_graph(5)
```

### Step 2: Assign starting_node = graph.add_node(...)

```python
starting_node = graph.add_node('starting node')
```

### Step 3: Call graph.add_edge()

```python
graph.add_edge(starting_node, 0, 'starting edge')
```

### Step 4: Assign sorter = rustworkx.TopologicalSorter(...)

```python
sorter = rustworkx.TopologicalSorter(graph, check_cycle=False)
```

### Step 5: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(nodes, [starting_node])
```

### Step 7: Call sorter.done()

```python
sorter.done(nodes)
```

### Step 8: Call self.assertFalse()

```python
self.assertFalse(sorter.is_active())
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_cycle_graph(5)
starting_node = graph.add_node('starting node')
graph.add_edge(starting_node, 0, 'starting edge')
sorter = rustworkx.TopologicalSorter(graph, check_cycle=False)
nodes = sorter.get_ready()
self.assertEqual(nodes, [starting_node])
sorter.done(nodes)
self.assertFalse(sorter.is_active())
```

## Next Steps


---

*Source: test_toposort.py:95 | Complexity: Advanced | Last updated: 2026-05-05*