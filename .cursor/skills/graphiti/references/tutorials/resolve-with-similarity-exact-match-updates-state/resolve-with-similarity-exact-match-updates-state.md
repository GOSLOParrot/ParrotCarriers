# How To: Resolve With Similarity Exact Match Updates State

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test resolve with similarity exact match updates state

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

### Step 1: Assign candidate = EntityNode(...)

```python
candidate = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
```

**Verification:**
```python
assert state.resolved_nodes[0].uuid == candidate.uuid
```

### Step 2: Assign extracted = EntityNode(...)

```python
extracted = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
```

**Verification:**
```python
assert state.uuid_map[extracted.uuid] == candidate.uuid
```

### Step 3: Assign indexes = _build_candidate_indexes(...)

```python
indexes = _build_candidate_indexes([candidate])
```

**Verification:**
```python
assert state.unresolved_indices == []
```

### Step 4: Assign state = DedupResolutionState(...)

```python
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])
```

**Verification:**
```python
assert state.duplicate_pairs == [(extracted, candidate)]
```

### Step 5: Call _resolve_with_similarity()

```python
_resolve_with_similarity([extracted], indexes, state)
```

**Verification:**
```python
assert state.resolved_nodes[0].uuid == candidate.uuid
```


## Complete Example

```python
# Workflow
candidate = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
extracted = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
indexes = _build_candidate_indexes([candidate])
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0].uuid == candidate.uuid
assert state.uuid_map[extracted.uuid] == candidate.uuid
assert state.unresolved_indices == []
assert state.duplicate_pairs == [(extracted, candidate)]
```

## Next Steps


---

*Source: test_node_operations.py:237 | Complexity: Intermediate | Last updated: 2026-04-12*