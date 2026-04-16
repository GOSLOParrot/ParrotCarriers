# How To: Two Tables Split Into Two Groups

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test two tables split into two groups

## Prerequisites

**Required Modules:**
- `nanobot.channels.feishu`
- `nanobot.channels`
- `pytest`


## Step-by-Step Guide

### Step 1: Assign t1 = value

```python
t1 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'A', 'width': 'auto'}], 'rows': [{'c0': 'table-one'}], 'page_size': 2}
```

**Verification:**
```python
assert len(result) == 2
```

### Step 2: Assign t2 = value

```python
t2 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'B', 'width': 'auto'}], 'rows': [{'c0': 'table-two'}], 'page_size': 2}
```

**Verification:**
```python
assert t1 in result[0]
```

### Step 3: Assign els = value

```python
els = [_md('before'), t1, _md('between'), t2, _md('after')]
```

**Verification:**
```python
assert t2 not in result[0]
```

### Step 4: Assign result = split(...)

```python
result = split(els)
```

**Verification:**
```python
assert t2 in result[1]
```


## Complete Example

```python
# Workflow
t1 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'A', 'width': 'auto'}], 'rows': [{'c0': 'table-one'}], 'page_size': 2}
t2 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'B', 'width': 'auto'}], 'rows': [{'c0': 'table-two'}], 'page_size': 2}
els = [_md('before'), t1, _md('between'), t2, _md('after')]
result = split(els)
assert len(result) == 2
assert t1 in result[0]
assert t2 not in result[0]
assert t2 in result[1]
assert t1 not in result[1]
```

## Next Steps


---

*Source: test_feishu_table_split.py:56 | Complexity: Intermediate | Last updated: 2026-04-12*