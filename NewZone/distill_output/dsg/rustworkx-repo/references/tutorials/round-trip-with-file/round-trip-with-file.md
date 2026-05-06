# How To: Round Trip With File

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test round trip with file

## Prerequisites

**Required Modules:**
- `json`
- `tempfile`
- `uuid`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.path_graph(...)

```python
graph = rustworkx.generators.path_graph(3)
```

### Step 2: Assign graph.attrs = 'path_graph'

```python
graph.attrs = 'path_graph'
```

### Step 3: Call self.assertIsInstance()

```python
self.assertIsInstance(new, type(graph))
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(new.nodes(), graph.nodes())
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(new.attrs, graph.attrs)
```

### Step 7: Assign unknown = value

```python
graph[node] = {'nodeLabel': f'node={node}'}
```

### Step 8: Call graph.update_edge_by_index()

```python
graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
```

### Step 9: Call rustworkx.node_link_json()

```python
rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
```

### Step 10: Assign new = rustworkx.from_node_link_json_file(...)

```python
new = rustworkx.from_node_link_json_file(fd.name, graph_attrs=lambda x: x['label'])
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name, graph_attrs=lambda x: x['label'])
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, graph.attrs)
```

## Next Steps


---

*Source: test_node_link_json.py:154 | Complexity: Advanced | Last updated: 2026-05-05*