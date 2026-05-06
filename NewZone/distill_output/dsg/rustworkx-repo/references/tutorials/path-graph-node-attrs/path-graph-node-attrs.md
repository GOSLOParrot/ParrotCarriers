# How To: Path Graph Node Attrs

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test path graph node attrs

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

### Step 2: Assign res = rustworkx.node_link_json(...)

```python
res = rustworkx.node_link_json(graph, node_attrs=dict)
```

### Step 3: Assign expected = value

```python
expected = {'attrs': None, 'directed': False, 'links': [{'data': None, 'id': 0, 'source': 0, 'target': 1}, {'data': None, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(json.loads(res), expected)
```

### Step 5: Assign unknown = value

```python
graph[node] = {'nodeLabel': f'node={node}'}
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.path_graph(3)
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
res = rustworkx.node_link_json(graph, node_attrs=dict)
expected = {'attrs': None, 'directed': False, 'links': [{'data': None, 'id': 0, 'source': 0, 'target': 1}, {'data': None, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
self.assertEqual(json.loads(res), expected)
```

## Next Steps


---

*Source: test_node_link_json.py:44 | Complexity: Intermediate | Last updated: 2026-05-05*