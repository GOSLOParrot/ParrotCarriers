# How To: Write Key For All

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test write key for all

## Prerequisites

**Required Modules:**
- `unittest`
- `tempfile`
- `gzip`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_xml = self.HEADER.format(...)

```python
graph_xml = self.HEADER.format('\n            <key id="d0" for="all" attr.name="test" attr.type="string"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">I\'m a graph.</data>\n            <node id="n0">\n                <data key="d0">I\'m a node.</data>\n            </node>\n            <node id="n1">\n                <data key="d0">I\'m a node.</data>\n            </node>\n            <edge source="n0" target="n1">\n                <data key="d0">I\'m an edge.</data>\n            </edge>\n            </graph>\n            ')
```

### Step 2: Assign keys = value

```python
keys = [rustworkx.GraphMLKey('d0', rustworkx.GraphMLDomain.All, 'test', rustworkx.GraphMLType.String, None)]
```

### Step 3: Assign graph = value

```python
graph = graphml[0]
```

### Step 4: Assign nodes = value

```python
nodes = [{'id': 'n0', 'test': "I'm a node."}, {'id': 'n1', 'test': "I'm a node."}]
```

### Step 5: Assign edges = value

```python
edges = [('n0', 'n1', {'test': "I'm an edge."})]
```

### Step 6: Call self.assertGraphEqual()

```python
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': "I'm a graph."})
```

### Step 7: Call fd.write()

```python
fd.write(graph_xml)
```

### Step 8: Call fd.flush()

```python
fd.flush()
```

### Step 9: Assign graphml = rustworkx.read_graphml(...)

```python
graphml = rustworkx.read_graphml(fd.name)
```

### Step 10: Call rustworkx.write_graphml()

```python
rustworkx.write_graphml(graphml[0], fd.name, keys=keys)
```

### Step 11: Assign graphml = rustworkx.read_graphml(...)

```python
graphml = rustworkx.read_graphml(fd.name)
```


## Complete Example

```python
# Workflow
graph_xml = self.HEADER.format('\n            <key id="d0" for="all" attr.name="test" attr.type="string"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">I\'m a graph.</data>\n            <node id="n0">\n                <data key="d0">I\'m a node.</data>\n            </node>\n            <node id="n1">\n                <data key="d0">I\'m a node.</data>\n            </node>\n            <edge source="n0" target="n1">\n                <data key="d0">I\'m an edge.</data>\n            </edge>\n            </graph>\n            ')
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
keys = [rustworkx.GraphMLKey('d0', rustworkx.GraphMLDomain.All, 'test', rustworkx.GraphMLType.String, None)]
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graphml[0], fd.name, keys=keys)
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
nodes = [{'id': 'n0', 'test': "I'm a node."}, {'id': 'n1', 'test': "I'm a node."}]
edges = [('n0', 'n1', {'test': "I'm an edge."})]
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': "I'm a graph."})
```

## Next Steps


---

*Source: test_graphml.py:348 | Complexity: Advanced | Last updated: 2026-05-05*