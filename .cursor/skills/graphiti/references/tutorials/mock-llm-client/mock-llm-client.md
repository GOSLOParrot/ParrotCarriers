# How To: Mock Llm Client

**Difficulty**: Intermediate
**Estimated Time**: 5 minutes
**Tags**: pytest, mock

## Overview

Configuration example: Create a mock LLM

## Prerequisites

**Required Modules:**
- `datetime`
- `unittest.mock`
- `pytest`
- `graphiti_core.cross_encoder.client`
- `graphiti_core.edges`
- `graphiti_core.graphiti`
- `graphiti_core.llm_client`
- `graphiti_core.nodes`
- `tests.helpers_test`
- `uuid`
- `uuid`
- `uuid`


## Step-by-Step Guide

### Step 1: Assign mock_llm.generate_response.return_value = value

```python
mock_llm.generate_response.return_value = {'duplicate_facts': [], 'invalidate_facts': []}
```


## Complete Example

```python
# Workflow
mock_llm.generate_response.return_value = {'duplicate_facts': [], 'invalidate_facts': []}
```

## Next Steps


---

*Source: test_add_triplet.py:46 | Complexity: Intermediate | Last updated: 2026-04-12*