# How To: Isomorphic To Networkx

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test isomorphic to networkx

## Prerequisites

**Required Modules:**
- `unittest`
- `tempfile`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rx.generators.karate_club_graph(...)

```python
graph = rx.generators.karate_club_graph()
```

### Step 2: Call self.assertTrue()

```python
self.assertTrue(rx.is_isomorphic(graph, expected, node_matcher=node_matcher, edge_matcher=edge_matcher))
```

### Step 3: Call fd.write()

```python
fd.write(karate_xml)
```

### Step 4: Call fd.flush()

```python
fd.flush()
```

### Step 5: Assign expected = value

```python
expected = rx.read_graphml(fd.name)[0]
```

### Step 6: Assign unknown = value

```python
a, b = (b, a)
```

### Step 7: Assign unknown = value

```python
a, b = (b, a)
```


## Complete Example

```python
# Workflow
def node_matcher(a, b):
    if isinstance(a, dict):
        a, b = (b, a)
    return a == b['club']

def edge_matcher(a, b):
    if isinstance(a, dict):
        a, b = (b, a)
    return a == b['weight']
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(karate_xml)
    fd.flush()
    expected = rx.read_graphml(fd.name)[0]
graph = rx.generators.karate_club_graph()
self.assertTrue(rx.is_isomorphic(graph, expected, node_matcher=node_matcher, edge_matcher=edge_matcher))
```

## Next Steps


---

*Source: test_karate.py:20 | Complexity: Intermediate | Last updated: 2026-05-05*