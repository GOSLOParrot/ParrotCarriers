# How To: Round Trip Networkx

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test round trip networkx

## Prerequisites

**Required Modules:**
- `json`
- `tempfile`
- `uuid`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = nx.generators.path_graph(...)

```python
graph = nx.generators.path_graph(5)
```

### Step 2: Assign new = rustworkx.parse_node_link_json(...)

```python
new = rustworkx.parse_node_link_json(node_link_str)
```

### Step 3: Call self.assertIsInstance()

```python
self.assertIsInstance(new, rustworkx.PyGraph)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(new.num_nodes(), graph.number_of_nodes())
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(new.edge_list(), list(graph.edges()))
```

### Step 6: Assign node_link_str = json.dumps(...)

```python
node_link_str = json.dumps(nx.node_link_data(graph, edges='links'))
```

### Step 7: Assign node_link_str = json.dumps(...)

```python
node_link_str = json.dumps(nx.node_link_data(graph))
```


## Complete Example

```python
# Workflow
graph = nx.generators.path_graph(5)
try:
    node_link_str = json.dumps(nx.node_link_data(graph, edges='links'))
except TypeError:
    node_link_str = json.dumps(nx.node_link_data(graph))
new = rustworkx.parse_node_link_json(node_link_str)
self.assertIsInstance(new, rustworkx.PyGraph)
self.assertEqual(new.num_nodes(), graph.number_of_nodes())
self.assertEqual(new.edge_list(), list(graph.edges()))
```

## Next Steps


---

*Source: test_node_link_json.py:175 | Complexity: Advanced | Last updated: 2026-05-05*