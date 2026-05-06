# How To: Max Nodes Truncation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test max nodes truncation

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.code_graph.blast_radius`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.graph_engine`
- `superlocalmemory.code_graph.graph_store`
- `superlocalmemory.code_graph.models`
- `rustworkx`

**Setup Required:**
```python
# Fixtures: store, br
```

## Step-by-Step Guide

### Step 1: Assign hub = _node(...)

```python
hub = _node('hub', 'hub', 'mod.hub')
```

**Verification:**
```python
assert result.truncated is True
```

### Step 2: Assign targets = value

```python
targets = [_node(f't{i}', f't{i}', f'mod.t{i}') for i in range(20)]
```

**Verification:**
```python
assert total <= 5
```

### Step 3: Assign edges = value

```python
edges = [_edge(f'e{i}', 'hub', f't{i}') for i in range(20)]
```

### Step 4: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [hub] + targets, edges, _fr())
```

### Step 5: Assign result = br.compute(...)

```python
result = br.compute(seed_node_ids=['hub'], max_depth=1, max_nodes=5, direction='forward')
```

**Verification:**
```python
assert result.truncated is True
```

### Step 6: Assign total = value

```python
total = len(result.changed_nodes) + len(result.impacted_nodes)
```

**Verification:**
```python
assert total <= 5
```


## Complete Example

```python
# Setup
# Fixtures: store, br

# Workflow
hub = _node('hub', 'hub', 'mod.hub')
targets = [_node(f't{i}', f't{i}', f'mod.t{i}') for i in range(20)]
edges = [_edge(f'e{i}', 'hub', f't{i}') for i in range(20)]
store.store_file_nodes_edges('src/mod.py', [hub] + targets, edges, _fr())
result = br.compute(seed_node_ids=['hub'], max_depth=1, max_nodes=5, direction='forward')
assert result.truncated is True
total = len(result.changed_nodes) + len(result.impacted_nodes)
assert total <= 5
```

## Next Steps


---

*Source: test_blast_radius.py:178 | Complexity: Intermediate | Last updated: 2026-05-05*