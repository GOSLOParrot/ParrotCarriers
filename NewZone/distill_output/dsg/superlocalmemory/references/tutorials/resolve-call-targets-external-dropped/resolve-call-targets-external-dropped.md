# How To: Resolve Call Targets External Dropped

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Calls with no matching symbol should be dropped.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `pathlib`
- `pytest`
- `superlocalmemory.code_graph.config`
- `superlocalmemory.code_graph.models`
- `superlocalmemory.code_graph.resolver`

**Setup Required:**
```python
# Fixtures: tmp_path, config
```

## Step-by-Step Guide

### Step 1: 'Calls with no matching symbol should be dropped.'

```python
'Calls with no matching symbol should be dropped.'
```

**Verification:**
```python
assert len(resolved) == 0
```

### Step 2: Assign resolver = ImportResolver(...)

```python
resolver = ImportResolver(tmp_path, config)
```

### Step 3: Assign nodes = value

```python
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='a.py::foo', file_path='a.py')]
```

### Step 4: Assign edges = value

```python
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__external_func', file_path='a.py', line=5)]
```

### Step 5: Assign resolved = resolver.resolve_call_targets(...)

```python
resolved = resolver.resolve_call_targets(nodes, edges, {})
```

**Verification:**
```python
assert len(resolved) == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, config

# Workflow
'Calls with no matching symbol should be dropped.'
resolver = ImportResolver(tmp_path, config)
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='a.py::foo', file_path='a.py')]
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__external_func', file_path='a.py', line=5)]
resolved = resolver.resolve_call_targets(nodes, edges, {})
assert len(resolved) == 0
```

## Next Steps


---

*Source: test_resolver.py:208 | Complexity: Intermediate | Last updated: 2026-05-05*