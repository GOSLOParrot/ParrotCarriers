# How To: Keep Edges Multigraph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow:    ┌─┐            ┌─┐
 ┌─┤a├─┐        ┌─┤a├─┐
 │ └─┘ │        │ └─┘ │
 1     2   ──►  1     2
┌┴┐   ┌┴┐       │ ┌─┐ │
│b│   │c│       └─┤m├─┘
└─┘   └─┘         └─┘

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: '\n           ┌─┐            ┌─┐\n         ┌─┤a├─┐        ┌─┤a├─┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌┴┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └─┤m├─┘\n        └─┘   └─┘         └─┘\n        '

```python
'\n           ┌─┐            ┌─┐\n         ┌─┤a├─┐        ┌─┤a├─┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌┴┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └─┤m├─┘\n        └─┘   └─┘         └─┘\n        '
```

### Step 2: Assign dag = rustworkx.PyGraph(...)

```python
dag = rustworkx.PyGraph()
```

### Step 3: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 4: Assign node_b = dag.add_node(...)

```python
node_b = dag.add_node('b')
```

### Step 5: Assign node_c = dag.add_node(...)

```python
node_c = dag.add_node('c')
```

### Step 6: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, 1)
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(node_c, node_a, 2)
```

### Step 8: Assign node_m = dag.contract_nodes(...)

```python
node_m = dag.contract_nodes([node_b, node_c], 'm')
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual([node_a, node_m], dag.node_indexes())
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual({UndirectedEdge((node_a, node_m, 1)), UndirectedEdge((node_a, node_m, 2))}, set((UndirectedEdge(e) for e in dag.weighted_edge_list())))
```


## Complete Example

```python
# Workflow
'\n           ┌─┐            ┌─┐\n         ┌─┤a├─┐        ┌─┤a├─┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌┴┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └─┤m├─┘\n        └─┘   └─┘         └─┘\n        '
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_c, node_a, 2)
node_m = dag.contract_nodes([node_b, node_c], 'm')
self.assertEqual([node_a, node_m], dag.node_indexes())
self.assertEqual({UndirectedEdge((node_a, node_m, 1)), UndirectedEdge((node_a, node_m, 2))}, set((UndirectedEdge(e) for e in dag.weighted_edge_list())))
```

## Next Steps


---

*Source: test_contract_nodes.py:140 | Complexity: Advanced | Last updated: 2026-05-05*