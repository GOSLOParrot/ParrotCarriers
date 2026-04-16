# How To: Convert Datetime List And Tuple

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test datetime conversion in lists and tuples.

## Prerequisites

**Required Modules:**
- `os`
- `unittest`
- `datetime`
- `unittest.mock`
- `pytest`
- `graphiti_core.driver.driver`
- `graphiti_core.driver.falkordb_driver`
- `graphiti_core.driver.falkordb_driver`
- `graphiti_core.driver.falkordb_driver`
- `graphiti_core.driver.falkordb_driver`
- `graphiti_core.driver.falkordb_driver`


## Step-by-Step Guide

### Step 1: 'Test datetime conversion in lists and tuples.'

```python
'Test datetime conversion in lists and tuples.'
```

**Verification:**
```python
assert result_list[0] == 'test'
```

### Step 2: Assign test_datetime = datetime(...)

```python
test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
```

**Verification:**
```python
assert result_list[1] == test_datetime.isoformat()
```

### Step 3: Assign input_list = value

```python
input_list = ['test', test_datetime, ['nested', test_datetime]]
```

**Verification:**
```python
assert result_list[2][1] == test_datetime.isoformat()
```

### Step 4: Assign result_list = convert_datetimes_to_strings(...)

```python
result_list = convert_datetimes_to_strings(input_list)
```

**Verification:**
```python
assert isinstance(result_tuple, tuple)
```

### Step 5: Assign input_tuple = value

```python
input_tuple = ('test', test_datetime)
```

**Verification:**
```python
assert result_tuple[0] == 'test'
```

### Step 6: Assign result_tuple = convert_datetimes_to_strings(...)

```python
result_tuple = convert_datetimes_to_strings(input_tuple)
```

**Verification:**
```python
assert result_tuple[1] == test_datetime.isoformat()
```


## Complete Example

```python
# Workflow
'Test datetime conversion in lists and tuples.'
from graphiti_core.driver.falkordb_driver import convert_datetimes_to_strings
test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
input_list = ['test', test_datetime, ['nested', test_datetime]]
result_list = convert_datetimes_to_strings(input_list)
assert result_list[0] == 'test'
assert result_list[1] == test_datetime.isoformat()
assert result_list[2][1] == test_datetime.isoformat()
input_tuple = ('test', test_datetime)
result_tuple = convert_datetimes_to_strings(input_tuple)
assert isinstance(result_tuple, tuple)
assert result_tuple[0] == 'test'
assert result_tuple[1] == test_datetime.isoformat()
```

## Next Steps


---

*Source: test_falkordb_driver.py:325 | Complexity: Intermediate | Last updated: 2026-04-12*