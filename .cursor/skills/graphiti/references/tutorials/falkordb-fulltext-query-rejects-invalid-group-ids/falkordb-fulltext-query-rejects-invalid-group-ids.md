# How To: Falkordb Fulltext Query Rejects Invalid Group Ids

**Difficulty**: Intermediate
**Estimated Time**: 5 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test falkordb fulltext query rejects invalid group ids

## Prerequisites

**Required Modules:**
- `types`
- `unittest.mock`
- `pytest`
- `pydantic`
- `graphiti_core.driver.driver`
- `graphiti_core.driver.neo4j.operations.search_ops`
- `graphiti_core.errors`
- `graphiti_core.search.search`
- `graphiti_core.search.search_config`
- `graphiti_core.search.search_filters`
- `graphiti_core.search.search_utils`
- `graphiti_core.driver.falkordb_driver`


## Step-by-Step Guide

### Step 1: Assign driver = MagicMock(...)

```python
driver = MagicMock(spec=FalkorDriver)
```

### Step 2: Assign driver.sanitize.return_value = 'test'

```python
driver.sanitize.return_value = 'test'
```

### Step 3: Call FalkorDriver.build_fulltext_query()

```python
FalkorDriver.build_fulltext_query(driver, 'test', ['bad"group'])
```


## Complete Example

```python
# Workflow
from graphiti_core.driver.falkordb_driver import FalkorDriver
driver = MagicMock(spec=FalkorDriver)
driver.sanitize.return_value = 'test'
with pytest.raises(GroupIdValidationError, match='must contain only alphanumeric'):
    FalkorDriver.build_fulltext_query(driver, 'test', ['bad"group'])
```

## Next Steps


---

*Source: test_search_security.py:62 | Complexity: Intermediate | Last updated: 2026-04-12*