# How To: Resolve With Similarity Multiple Exact Matches Defers To Llm

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test resolve with similarity multiple exact matches defers to llm

## Prerequisites

**Required Modules:**
- `logging`
- `collections`
- `unittest.mock`
- `pytest`
- `graphiti_core.graphiti_types`
- `graphiti_core.nodes`
- `graphiti_core.search.search_config`
- `graphiti_core.utils.datetime_utils`
- `graphiti_core.utils.maintenance.dedup_helpers`
- `graphiti_core.utils.maintenance.node_operations`
- `graphiti_core.edges`
- `graphiti_core.utils.text_utils`


## Step-by-Step Guide

### Step 1: Assign candidate1 = EntityNode(...)

```python
candidate1 = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
```

**Verification:**
```python
assert state.resolved_nodes[0] is None
```

### Step 2: Assign candidate2 = EntityNode(...)

```python
candidate2 = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
```

**Verification:**
```python
assert state.unresolved_indices == [0]
```

### Step 3: Assign extracted = EntityNode(...)

```python
extracted = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
```

**Verification:**
```python
assert state.duplicate_pairs == []
```

### Step 4: Assign indexes = _build_candidate_indexes(...)

```python
indexes = _build_candidate_indexes([candidate1, candidate2])
```

### Step 5: Assign state = DedupResolutionState(...)

```python
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])
```

### Step 6: Call _resolve_with_similarity()

```python
_resolve_with_similarity([extracted], indexes, state)
```

**Verification:**
```python
assert state.resolved_nodes[0] is None
```


## Complete Example

```python
# Workflow
candidate1 = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
candidate2 = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
extracted = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
indexes = _build_candidate_indexes([candidate1, candidate2])
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0] is None
assert state.unresolved_indices == [0]
assert state.duplicate_pairs == []
```

## Next Steps


---

*Source: test_node_operations.py:270 | Complexity: Intermediate | Last updated: 2026-04-12*