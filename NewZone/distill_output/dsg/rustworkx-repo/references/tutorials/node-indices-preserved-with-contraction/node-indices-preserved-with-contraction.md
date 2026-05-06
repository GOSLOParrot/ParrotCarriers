# How To: Node Indices Preserved With Contraction

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that node indices are preserved after contraction (issue #1503)

## Prerequisites

**Required Modules:**
- `json`
- `tempfile`
- `uuid`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: 'Test that node indices are preserved after contraction (issue #1503)'

```python
'Test that node indices are preserved after contraction (issue #1503)'
```

### Step 2: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 3: Call graph.add_node()

```python
graph.add_node(None)
```

### Step 4: Call graph.add_node()

```python
graph.add_node(None)
```

### Step 5: Call graph.add_node()

```python
graph.add_node(None)
```

### Step 6: Assign contracted_idx = graph.contract_nodes(...)

```python
contracted_idx = graph.contract_nodes([0, 1], None)
```

### Step 7: Call graph.add_edge()

```python
graph.add_edge(2, contracted_idx, None)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual([2, contracted_idx], graph.node_indices())
```

### Step 9: Assign json_str = rustworkx.node_link_json(...)

```python
json_str = rustworkx.node_link_json(graph)
```

### Step 10: Assign restored = rustworkx.parse_node_link_json(...)

```python
restored = rustworkx.parse_node_link_json(json_str)
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(graph.node_indices(), restored.node_indices())
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(graph.edge_list(), restored.edge_list())
```


## Complete Example

```python
# Workflow
'Test that node indices are preserved after contraction (issue #1503)'
graph = rustworkx.PyGraph()
graph.add_node(None)
graph.add_node(None)
graph.add_node(None)
contracted_idx = graph.contract_nodes([0, 1], None)
graph.add_edge(2, contracted_idx, None)
self.assertEqual([2, contracted_idx], graph.node_indices())
json_str = rustworkx.node_link_json(graph)
restored = rustworkx.parse_node_link_json(json_str)
self.assertEqual(graph.node_indices(), restored.node_indices())
self.assertEqual(graph.edge_list(), restored.edge_list())
```

## Next Steps


---

*Source: test_node_link_json.py:228 | Complexity: Advanced | Last updated: 2026-05-05*